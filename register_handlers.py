from aiogram import Dispatcher, filters
from handlers.handlers import *
from states import RegisterTeamsStorage, GameStorage
from handlers.edit import register_edit_handlers


def handler_register(dp: Dispatcher) -> None:
    register_edit_handlers(dp)

    dp.register_message_handler(begin_match, commands="start")
    dp.register_message_handler(add_game_command_handler, commands='add')
    dp.register_callback_query_handler(register_state_handler, lambda c: c.data == 'begin_match')

    dp.register_callback_query_handler(register_first_color, lambda c: c.data.startswith(team_color.prefix), state=RegisterTeamsStorage.first)
    dp.register_callback_query_handler(register_second_color, lambda c: c.data.startswith(team_color.prefix), state=RegisterTeamsStorage.second)
    dp.register_callback_query_handler(register_third_color, lambda c: c.data.startswith(team_color.prefix), state=RegisterTeamsStorage.third)

    dp.register_message_handler(register_first_team, state=RegisterTeamsStorage.first)
    dp.register_message_handler(register_second_team, state=RegisterTeamsStorage.second)
    dp.register_message_handler(register_third_team, state=RegisterTeamsStorage.third)
    dp.register_callback_query_handler(add_game_handler, lambda c: c.data == "add_game")
    dp.register_callback_query_handler(choose_second_team, lambda c: c.data.startswith(team_callback.prefix), state=GameStorage.first_team)
    dp.register_callback_query_handler(show_controls_buttons, lambda c: c.data.startswith(team_callback.prefix), state=GameStorage.second_team)
    dp.register_callback_query_handler(
        get_controls_answer,
        lambda c: c.data.startswith(plus_team_score.prefix) or c.data.startswith(minus_team_score.prefix),
        state=GameStorage.results
    )


    #dp.register_message_handler(get_second_team_result, state=GameStorage.first_result)
    dp.register_callback_query_handler(write_game_results,
                                       lambda c: c.data == "finish_game",
                                       state=GameStorage.results)
    dp.register_callback_query_handler(show_statistic, lambda c: c.data == 'finish_match')

    dp.register_callback_query_handler(delete_message_handler,
                                       lambda c: c.data == 'delete_message',
                                       state='*')


