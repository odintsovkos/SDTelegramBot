"""
Автор: Константин Одинцов
e-mail: kos5172@yandex.ru
Github: https://github.com/odintsovkos
Этот файл — часть SDTelegramBot.

SDTelegramBot — свободная программа: вы можете перераспространять ее и/или изменять ее на условиях Стандартной общественной лицензии GNU в том виде, в каком она была опубликована Фондом свободного программного обеспечения; либо версии 3 лицензии, либо (по вашему выбору) любой более поздней версии.

SDTelegramBot распространяется в надежде, что она будет полезной, но БЕЗО ВСЯКИХ ГАРАНТИЙ; даже без неявной гарантии ТОВАРНОГО ВИДА или ПРИГОДНОСТИ ДЛЯ ОПРЕДЕЛЕННЫХ ЦЕЛЕЙ. Подробнее см. в Стандартной общественной лицензии GNU.

Вы должны были получить копию Стандартной общественной лицензии GNU вместе с этой программой. Если это не так, см. <https://www.gnu.org/licenses/>.
"""


import logging

from aiogram import Dispatcher

from settings.bot_config import ADMINS, USERS


async def admin_notify(dp: Dispatcher, msg: str):
    for admin in ADMINS:
        try:
            await dp.bot.send_message(admin, msg)

        except Exception as err:
            logging.exception(err)


async def user_notify(dp: Dispatcher, msg: str):
    for user in USERS:
        try:
            await dp.bot.send_message(user, msg)

        except Exception as err:
            logging.exception(err)


async def users_and_admins_notify(dp: Dispatcher, msg: str):
    await user_notify(dp, msg)
    await admin_notify(dp, msg)
