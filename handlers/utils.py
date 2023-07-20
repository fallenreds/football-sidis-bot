from aiogram import types
from aiogram.utils.callback_data import CallbackData
from aiogram.dispatcher import FSMContext
from settings import bot, AVAILABLE_COLORS
from states import RegisterTeamsStorage, GameStorage
from data_csv_engine import register_teams, read_headers, add_team_results, calculate_all_games, get_all_rows, \
    edit_team_results

from callbacks import *

async def get_controls_keyboard(state:FSMContext):
    state_data = await state.get_data()
    kb = types.InlineKeyboardMarkup()
    minus_buttons = [
            types.InlineKeyboardButton(
                f"{state_data['first_team']}(-1)",
                callback_data=minus_team_score.new("first_result")

        ),
            types.InlineKeyboardButton(
                f"{state_data['second_team']}(-1)",
                callback_data=minus_team_score.new("second_result")
            )

    ]
    plus_buttons = [
        types.InlineKeyboardButton(
            f"{state_data['first_team']}(+1)",
            callback_data=plus_team_score.new("first_result")
        ),
        types.InlineKeyboardButton(
            f"{state_data['second_team']}(+1)",
            callback_data=plus_team_score.new("second_result")
        )
    ]
    kb.add(
        *plus_buttons
    )
    kb.add(
        *minus_buttons
    )
    kb.add(
        types.InlineKeyboardButton(
            "Завершити гру",
            callback_data="finish_game"
        )
    )
    return kb
async def get_controls_answer(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    state_data = await state.get_data()
    if callback.data.startswith(plus_team_score.prefix):
        team_key = plus_team_score.parse(callback.data)['team_key']
        async with state.proxy() as data:
            data[team_key] = int(state_data[team_key])+1
    if callback.data.startswith(minus_team_score.prefix):
        team_key = minus_team_score.parse(callback.data)['team_key']
        async with state.proxy() as data:
            if int(state_data[team_key])>0:
                data[team_key] = int(state_data[team_key])-1

    state_data = await state.get_data()
    kb = await get_controls_keyboard(state)
    return await bot.send_message(callback.message.chat.id, f"{state_data['first_team']} vs {state_data['second_team']}"
                                                            f"({state_data['first_result']}:{state_data['second_result']})",
                                  reply_markup=kb)

def set_delimiter(delimiter: str, data: list):
    return f"{delimiter.join(data)}"