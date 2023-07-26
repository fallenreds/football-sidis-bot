from aiogram import Dispatcher
from aiogram import types
from aiogram.dispatcher import FSMContext

from buttons import DELETE_BUTTON
from callbacks import *
from data_csv_engine import read_headers, get_all_rows, \
    edit_team_results
from handlers.handlers import add_or_finish_match
from handlers.utils import get_controls_keyboard, set_delimiter, get_controls_answer
from settings import bot
from states import EditGameStorage


async def edit_games_command_handler(message: types.Message):
    await message.delete()

    try:
        all_rows = await get_all_rows(message.chat.id)
    except FileNotFoundError:
        return await add_or_finish_match(message)
    await EditGameStorage.first_team.set()
    kb = types.InlineKeyboardMarkup()

    for index, game in enumerate(all_rows[1:]):
        kb.add(
            types.InlineKeyboardButton(
                f"{index + 1}--{game}",
                callback_data=edit_game_callback.new(index + 1)
            )
        )
    kb.add(DELETE_BUTTON)
    text = "Натисніть на гру, яку хочете редагувати"
    await bot.send_message(message.chat.id, text=text, reply_markup=kb)


async def edit_game_handler(callback: types.CallbackQuery, state: FSMContext):
    row_number = edit_game_callback.parse(callback.data)['row_number']
    await state.update_data(row_number=row_number)
    teams = await read_headers(callback.message.chat.id)
    return await choose_first_team(callback, teams)


async def choose_first_team(callback, available_teams):
    keyboard_button_container = types.InlineKeyboardMarkup(resize_keyboard=True)
    for team in available_teams:
        keyboard_button_container.add(types.InlineKeyboardButton(team, callback_data=team_callback.new(team)))
    await EditGameStorage.first_team.set()
    return await callback.message.edit_text("Оберіть першу команду", reply_markup=keyboard_button_container)


async def choose_second_team(callback: types.CallbackQuery, state: FSMContext):
    team_label = team_callback.parse(callback.data)['team_label']
    available_teams = await read_headers(callback.message.chat.id)
    available_teams.remove(team_label)
    async with state.proxy() as data:
        data['first_team'] = team_label
    await EditGameStorage.next()

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
    await EditGameStorage.next()

    kb = await get_controls_keyboard(state)

    return await callback.message.edit_text(f"{state_data['first_team']} vs {state_data['first_team']}"
                                            f"({state_data['first_result']}:{state_data['second_result']})",
                                            reply_markup=kb)


async def edit_game_results(callback: types.CallbackQuery,
                            state: FSMContext
                            ):
    results = await state.get_data()
    row_number = results['row_number']
    row_index = len(await get_all_rows(callback.message.chat.id))

    await state.finish()
    results_in_order = await edit_team_results(results, int(row_number), callback.message.chat.id)
    teams = await read_headers(callback.message.chat.id)
    response = f"{set_delimiter('-', teams)}\n{row_index - 1}) {set_delimiter('-', results_in_order)}"
    kb = types.InlineKeyboardMarkup()
    kb.add(DELETE_BUTTON)
    await callback.message.edit_text(response, reply_markup=kb)
    return await add_or_finish_match(callback.message)


def register_edit_handlers(dp: Dispatcher):
    dp.register_message_handler(edit_games_command_handler, commands='edit')
    dp.register_callback_query_handler(
        edit_game_handler,
        lambda c: c.data.startswith(edit_game_callback.prefix),
        state=EditGameStorage.first_team
    )
    dp.register_callback_query_handler(
        choose_second_team,
        lambda c: c.data.startswith(team_callback.prefix),
        state=EditGameStorage.first_team)

    dp.register_callback_query_handler(
        show_controls_buttons,
        lambda c: c.data.startswith(team_callback.prefix),
        state=EditGameStorage.second_team
    )
    dp.register_callback_query_handler(
        get_controls_answer,
        lambda c: c.data.startswith(plus_team_score.prefix) or c.data.startswith(minus_team_score.prefix),
        state=EditGameStorage.results
    )
    dp.register_callback_query_handler(edit_game_results, lambda c: c.data == "finish_game",
                                       state=EditGameStorage.results)
