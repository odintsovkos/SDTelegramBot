"""
Автор: Константин Одинцов
e-mail: kos5172@yandex.ru
Github: https://github.com/odintsovkos
Этот файл — часть SDTelegramBot.

SDTelegramBot — свободная программа: вы можете перераспространять ее и/или изменять ее на условиях Стандартной общественной лицензии GNU в том виде, в каком она была опубликована Фондом свободного программного обеспечения; либо версии 3 лицензии, либо (по вашему выбору) любой более поздней версии.

SDTelegramBot распространяется в надежде, что она будет полезной, но БЕЗО ВСЯКИХ ГАРАНТИЙ; даже без неявной гарантии ТОВАРНОГО ВИДА или ПРИГОДНОСТИ ДЛЯ ОПРЕДЕЛЕННЫХ ЦЕЛЕЙ. Подробнее см. в Стандартной общественной лицензии GNU.

Вы должны были получить копию Стандартной общественной лицензии GNU вместе с этой программой. Если это не так, см. <https://www.gnu.org/licenses/>.
"""


import asyncio
import time

import aiogram

from loader import bot

async def waiting_bar_trascribe_audio(chat_id: int, future):
    list_items = ["🟩", "⬜️", "⬜️", "⬜️", "⬜️"]
    green_item = "🟩"
    gray_item = "⬜️"
    num = 0
    direction = True

    upload_message = await bot.send_message(chat_id=chat_id, text=''.join(list_items) + " 0s")
    await asyncio.sleep(0.5)
    last_time = time.time()
    while True:
        if num == 4:
            direction = False
        elif num == 0:
            direction = True
        if direction:
            num += 1
            list_items[num - 1] = gray_item
            list_items[num] = green_item
        else:
            num -= 1
            list_items[num + 1] = gray_item
            list_items[num] = green_item
        if not future.done():
            prog = ''.join(list_items)
            try:
                await upload_message.edit_text(text=prog + f" {round(time.time() - last_time)}s.")
            except aiogram.exceptions.MessageNotModified:
                continue
            await asyncio.sleep(0.2)
        else:
            break
    return upload_message.chat.id, upload_message.message_id


async def waiting_bar(chat_id, thread):
    list_items = ["🟩", "⬜️", "⬜️", "⬜️", "⬜️"]
    green_item = "🟩"
    gray_item = "⬜️"
    num = 0
    direction = True

    upload_message = await bot.send_message(chat_id=chat_id, text=''.join(list_items) + " 0s")
    await asyncio.sleep(0.5)
    last_time = time.time()
    while True:
        if num == 4:
            direction = False
        elif num == 0:
            direction = True
        if direction:
            num += 1
            list_items[num - 1] = gray_item
            list_items[num] = green_item
        else:
            num -= 1
            list_items[num + 1] = gray_item
            list_items[num] = green_item
        if thread.is_alive():
            prog = ''.join(list_items)
            try:
                await upload_message.edit_text(text=prog + f" {round(time.time() - last_time)}s.")
            except aiogram.exceptions.MessageNotModified:
                continue
            await asyncio.sleep(0.2)
        else:
            break
    return upload_message.chat.id, upload_message.message_id
