import asyncio

import aiogram

from loader import bot
from utils.sd_api import api_service


async def progress_bar(chat_id, thread):
    list_items = ["⬜️", "⬜️", "⬜️", "⬜️", "⬜️", "⬜️", "⬜️", "⬜️", "⬜️", "⬜️"]
    green_item = "🟩"
    num = 0
    lust_num = 0
    lust_percent_num = 0

    upload_message = await bot.send_message(chat_id=chat_id, text=''.join(list_items) + " 0%")
    await asyncio.sleep(0.5)

    while True:
        if 0 <= num <= 1:
            list_items[0] = green_item
        else:
            for i in range(lust_num, num):
                list_items[i] = green_item

        if thread.is_alive():
            progress = api_service.get_request_sd_api("progress")
            progress_percent = round(progress.json()['progress'] * 100)
            if progress_percent == 0 and num != 0:
                progress_percent = 100
            lust_num = num
            num = int(progress_percent / 10)
            prog = ''.join(list_items)
            if progress_percent != lust_percent_num:
                try:
                    await upload_message.edit_text(prog + " " + str(progress_percent) + "%")
                except aiogram.exceptions.MessageNotModified:
                    continue
                lust_percent_num = progress_percent
            await asyncio.sleep(0.1)
        else:
            if num <= 10:
                try:
                    await upload_message.edit_text(''.join(list_items) + " 100%")
                except aiogram.exceptions.MessageNotModified:
                    break
            break
    return upload_message.chat.id, upload_message.message_id
