from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from callbacks import *
from data_csv_engine import read_headers, is_registered
from handlers.register import register_state_handler
from handlers.utils import get_controls_keyboard, get_controls_answer, add_or_finish_match
from settings import bot
from states import GameStorage


async def add_game_command_handler(message: types.Message):
    if not await is_registered(message.chat.id):
        return await add_or_finish_match(message)
    callback = types.CallbackQuery()
    callback.message = message
    await add_game_handler(callback)


async def add_game_handler(callback: types.CallbackQuery):
    try:
        teams = await read_headers(callback.message.chat.id)
        return await choose_first_team(callback, teams)
    except FileNotFoundError:
        await register_state_handler(callback)

async def choose_first_team(callback, available_teams):
    await callback.message.delete()
    keyboard_button_container = types.InlineKeyboardMarkup(resize_keyboard=True)
    for team in available_teams:
        keyboard_button_container.add(types.InlineKeyboardButton(team, callback_data=team_callback.new(team)))
    await GameStorage.first_team.set()
    return await bot.send_message(callback.message.chat.id, "Оберіть першу команду",
                                  reply_markup=keyboard_button_container)


async def choose_second_team(callback: types.CallbackQuery, state: FSMContext):
    team_label = team_callback.parse(callback.data)['team_label']
    available_teams = await read_headers(callback.message.chat.id)
    available_teams.remove(team_label)
    async with state.proxy() as data:
        data['first_team'] = team_label
    await GameStorage.next()
    keyboard_button_container = types.InlineKeyboardMarkup(resize_keyboard=True)
    for team in available_teams:
        keyboard_button_container.add(types.InlineKeyboardButton(team, callback_data=team_callback.new(team)))
    return await callback.message.edit_text("Оберіть другу команду команду", reply_markup=keyboard_button_container)



async def show_controls_buttons(callback: types.CallbackQuery, state: FSMContext):
    team_label = team_callback.parse(callback.data)['team_label']
    async with state.proxy() as data:
        data['second_team'] = team_label

    await state.update_data(first_result=0)
    await state.update_data(second_result=0)
    state_data = await state.get_data()
    await GameStorage.next()

    kb = await get_controls_keyboard(state)

    return await callback.message.edit_text(f"{state_data['first_team']} vs {state_data['second_team']}"
                                                            f"({state_data['first_result']}:{state_data['second_result']})",
                                  reply_markup=kb)



def register_add_handlers(dp: Dispatcher):
    dp.register_message_handler(add_game_command_handler, commands='add')
    dp.register_callback_query_handler(add_game_handler, lambda c: c.data == "add_game")
    dp.register_callback_query_handler(choose_second_team, lambda c: c.data.startswith(team_callback.prefix), state=GameStorage.first_team)
    dp.register_callback_query_handler(show_controls_buttons, lambda c: c.data.startswith(team_callback.prefix), state=GameStorage.second_team)
    dp.register_callback_query_handler(
        get_controls_answer,
        lambda c: c.data.startswith(plus_team_score.prefix) or c.data.startswith(minus_team_score.prefix),
        state=GameStorage.results
    )