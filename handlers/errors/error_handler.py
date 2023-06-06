import logging
from aiogram.utils.exceptions import (TelegramAPIError,
                                      MessageNotModified,
                                      CantParseEntities)


from loader import dp


@dp.errors_handler()
async def errors_handler(update, exception):
    """
    Exceptions handler. Catches all exceptions within task factory tasks.
    :param dispatcher:
    :param update:
    :param exception:
    :return: stdout logging
    """


    if isinstance(exception, MessageNotModified):
        logging.exception('Message is not modified')
        # do something here?
        return True
      
    if isinstance(exception, CantParseEntities):
        # or here
        logging.exception(f'CantParseEntities: {exception} \nUpdate: {update}')
        return True
      
    #  MUST BE THE  LAST CONDITION (ЭТО УСЛОВИЕ ВСЕГДА ДОЛЖНО БЫТЬ В КОНЦЕ)
    if isinstance(exception, TelegramAPIError):
        logging.exception(f'TelegramAPIError: {exception} \nUpdate: {update}')
        return True
    
    # At least you have tried.
    logging.exception(f'Update: {update} \n{exception}')
