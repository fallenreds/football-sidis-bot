from aiogram import Dispatcher
from aiogram.dispatcher.filters import ExceptionsFilter

from handlers.add import register_add_handlers
from handlers.edit import register_edit_handlers
from handlers.handlers import *
from handlers.register import register_register_handlers
from states import GameStorage


def handler_register(dp: Dispatcher) -> None:
    dp.register_message_handler(begin_match, commands="start")



    register_edit_handlers(dp)
    register_register_handlers(dp)
    register_add_handlers(dp)

    dp.register_message_handler(reload, commands=['reload'], state="*")
    dp.register_callback_query_handler(write_game_results,
                                       lambda c: c.data == "finish_game",
                                       state=GameStorage.results)
    dp.register_callback_query_handler(show_statistic, lambda c: c.data == 'get_stat')

    dp.register_callback_query_handler(delete_message_handler,
                                       lambda c: c.data == 'delete_message',
                                       state='*')
    dp.register_callback_query_handler(exit_from_state,
                                       lambda c: c.data == 'exit_from_state',
                                       state='*')
    dp.register_errors_handler(error_handler)
