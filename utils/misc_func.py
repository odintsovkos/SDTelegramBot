import asyncio
import base64
import io
import logging
import os
import threading
import time
import ast
import psutil as psutil
from aiogram import types

from keyboards.default import keyboards
from loader import dp
from settings.bot_config import sd_path
from settings.sd_config import save_files, output_folder
from utils.db_services import db_service
from utils.notifier import admin_notify, users_and_admins_notify
from utils.progress_bar import progress_bar
from utils.sd_api import api_service
from utils.sd_api.api_service import get_request_sd_api


async def generate_image(tg_id: int, last_prompt, seed):
    db_result = await db_service.db_get_sd_settings(tg_id)
    params = {
        "prompt": last_prompt,
        "negative_prompt": db_result[4],
        "styles": db_result[2].split('&'),
        "cfg_scale": db_result[8],
        "steps": db_result[6],
        "width": int(db_result[7].split('x')[0]),
        "height": int(db_result[7].split('x')[1]),
        "sampler_name": db_result[5],
        "restore_faces": 'true' if db_result[9] else 'false',
        "batch_size": db_result[10],
        "save_images": 'true' if save_files else 'false',
        "seed": seed
    }
    if save_files:
        api_service.post_request_sd_api("options", {"outdir_txt2img_samples": f"{output_folder}"})
    response = api_service.post_request_sd_api("txt2img", params)
    return response


async def change_sd_model(tg_id: int):
    sd_model = api_service.get_request_sd_api("options").json()['sd_model_checkpoint']
    db_model = await db_service.db_get_sd_setting(tg_id, "sd_model")
    if db_model != sd_model:
        params = {
            "sd_model_checkpoint": db_model
        }
        api_service.post_request_sd_api("options", params)
        return db_model
    else:
        return db_model


def is_sd_launched():
    response = get_request_sd_api("options", is_logging=False)
    if response is None:
        return False
    else:
        return True


async def change_style_db(tg_id: int, entered_style):
    db_styles_list = await db_service.db_get_sd_setting(tg_id, 'sd_style')
    if db_styles_list == "":
        await db_service.db_set_sd_settings(tg_id, 'sd_style', entered_style)
        return True
    else:
        result = db_styles_list.split('&')
        if entered_style not in result:
            result = db_styles_list + '&' + entered_style
            await db_service.db_set_sd_settings(tg_id, 'sd_style', result)
            return True
        else:
            result.remove(entered_style)
            await db_service.db_set_sd_settings(tg_id, 'sd_style', '&'.join(result))
            return False


async def change_lora_db(tg_id: int, entered_lora):
    db_lora_list = await db_service.db_get_sd_setting(tg_id, 'sd_lora')
    if db_lora_list == "":
        await db_service.db_set_sd_settings(tg_id, 'sd_lora', entered_lora)
        return True
    else:
        result = db_lora_list.split('&')
        if entered_lora not in result:
            result = db_lora_list + '&' + entered_lora
            await db_service.db_set_sd_settings(tg_id, 'sd_lora', result)
            return True
        else:
            result.remove(entered_lora)
            await db_service.db_set_sd_settings(tg_id, 'sd_lora', '&'.join(result))
            return False


async def user_samplers(api_samplers, hide_user_samplers):
    return [x for x in api_samplers if x['name'] not in hide_user_samplers]


async def reformat_lora(lora):
    lora_list = lora.split('&')
    if lora == "":
        return lora
    else:
        result = (f'<lora:{x}:0.7>' for x in lora_list)
        return ', '.join(result)


async def kill_sd_process():
    for proc in psutil.process_iter():
        if proc.name() == "python.exe" and proc.cmdline()[1] == "launch.py":
            pid = proc.pid
            os.system(f"taskkill /Pid {pid} /f")
            await asyncio.sleep(1)
    for proc in psutil.process_iter():
        if proc.name() == "cmd.exe" and "webui-user.bat" in proc.cmdline():
            pid = proc.pid
            os.system(f"taskkill /Pid {pid} /f")
            await asyncio.sleep(1)


def start_sd_process():
    os.system(f"cd {sd_path} && start webui-user.bat")


def check_sd_path():
    list_files = ""
    if sd_path != "":
        try:
            list_files = os.listdir(sd_path)
            if "webui-user.bat" in list_files:
                return True
            else:
                logging.warning("Не найден файл webui-user.bat, проверь путь в config.")
                return False
        except FileNotFoundError:
            logging.warning("Путь к папке SD не верный, проверь путь в bot_config.py")
            return False
    else:
        logging.warning("Путь к папке SD не указан в файле bot_config.py")
        return False


async def restart_sd():
    await kill_sd_process()
    start_sd_process()


def generate_image_callback(user_id, prompt, seed, response):
    loop = asyncio.run(generate_image(tg_id=user_id, last_prompt=prompt, seed=seed))
    response.append(loop)
    return loop


def change_model_callback(user_id, response):
    loop = asyncio.run(change_sd_model(user_id))
    response.append(loop)
    return loop


async def send_photo(message, last_prompt, response_list):
    sd_model = await change_sd_model(message.from_user.id)
    lora = await db_service.db_get_sd_setting(message.from_user.id, 'sd_lora')
    seed, prompt = await message_parse(last_prompt)
    thread_generate_image = threading.Thread(target=generate_image_callback, args=(
        message.from_user.id, await reformat_lora(lora) + ", " + prompt, seed, response_list))
    thread_generate_image.start()

    chat_id, message_id = await progress_bar(message.chat.id, thread_generate_image)

    thread_generate_image.join()

    style = await db_service.db_get_sd_setting(message.from_user.id, 'sd_style')
    style_caption = f"\n<b>Styles: </b><i>{style.replace('&', ', ')}</i>"
    lora_caption = f"\n<b>LoRa: </b><i>{lora.replace('&', ', ')}</i>"
    caption = f"<b>Positive prompt:</b>\n<code>{prompt}</code>\n" \
              f"<b>Model:</b>\n<i>{sd_model}</i>"
    if style != '':
        caption += style_caption
    if lora != '':
        caption += lora_caption

    if response_list[0] is not None:
        media = types.MediaGroup()
        if len(response_list[0]['images']) > 1:
            try:
                count = 1
                for i in response_list[0]['images']:
                    image = types.InputFile(io.BytesIO(base64.b64decode(i.split(",", 1)[0])))
                    media.attach_photo(image)
                    image_seed = api_service.get_image_seed(i)
                    caption += f"\n<b>Seed {count}:</b> <code>{image_seed}</code>"
                    count += 1
                await message.bot.delete_message(chat_id=chat_id, message_id=message_id)
                await message.answer_media_group(media=media)
                await message.answer(caption, reply_markup=keyboards.main_menu)
            except Exception as err:
                await message.answer("Ошибка генерации фото, информация об ошибке уже передана администраторам",
                                     reply_markup=keyboards.main_menu)
                await admin_notify(dp, msg="[ERROR] Ошибка генерации фото\n" + str(err))
        else:
            for i in response_list[0]['images']:
                image = types.InputFile(io.BytesIO(base64.b64decode(i.split(",", 1)[0])))
                image_seed = api_service.get_image_seed(i)
                caption += f"\n<b>Seed:</b>\n<code>{image_seed}</code>"
                await message.bot.delete_message(chat_id=chat_id, message_id=message_id)
                await message.answer_photo(photo=image)
                await message.answer(caption, reply_markup=keyboards.main_menu)
    else:
        await message.answer("Ошибка генерации фото, информация об ошибке уже передана администраторам",
                             reply_markup=keyboards.main_menu)
        await admin_notify(dp,
                           msg="[ERROR] Ошибка генерации фото\n Ошибка в функции send_photo " + str(response_list[0]))
    response_list.clear()


async def restarting_sd(message):
    await message.answer("⛔️ SD не отвечает...\n🔃 Перезапускаю SD!", reply_markup=keyboards.main_menu)
    await restart_sd()
    start_time = time.time()
    while True:
        if is_sd_launched():
            current_time = time.time()
            logging.info(f"SD запущена - {int(current_time - start_time)}s.")
            await users_and_admins_notify(dp, f"✅ SD запущена - {int(current_time - start_time)}s.")
            break
        await asyncio.sleep(1)


async def message_parse(message):
    if message.find('&') != -1:
        message_list = message.split('&')
        return message_list[0], message_list[1]
    else:
        return -1, message
