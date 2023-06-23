from aiogram import Dispatcher, filters
from handlers import *
from states import RegisterTeamsStorage, GameStorage



def handler_register(dp: Dispatcher) -> None:
    dp.register_message_handler(begin_match, commands="start")
    dp.register_callback_query_handler(register_state_handler, lambda c: c.data == 'begin_match')
    dp.register_message_handler(register_first_team, state=RegisterTeamsStorage.first)
    dp.register_message_handler(register_second_team, state=RegisterTeamsStorage.second)
    dp.register_message_handler(register_third_team, state=RegisterTeamsStorage.third)
    dp.register_callback_query_handler(add_game_handler, lambda c: c.data == "add_game")
    dp.register_callback_query_handler(choose_second_team, lambda c: c.data.startswith(team_callback.prefix), state=GameStorage.first_team)
    dp.register_callback_query_handler(get_first_team_result, lambda c: c.data.startswith(team_callback.prefix), state=GameStorage.second_team)
    dp.register_message_handler(get_second_team_result, state=GameStorage.first_result)
    dp.register_message_handler(write_game_results, state=GameStorage.second_result)
    dp.register_callback_query_handler(show_statistic, lambda c: c.data == 'finish_match')


