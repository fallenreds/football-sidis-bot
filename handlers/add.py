from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from workers.tournament import TournamentWorker
from callbacks import *
from data_csv_engine import read_headers, is_registered
from handlers.register import register_state_handler
from handlers.utils import get_controls_keyboard, get_controls_answer, add_or_finish_match
from settings import bot
from states import GameStorage


async def add_game_command_handler(message: types.Message):

    async with TournamentWorker() as worker:
        if not await worker.is_registered_tournament(message.chat.id):
            return await add_or_finish_match(message)
        callback = types.CallbackQuery()
        callback.message = message
        await add_game_handler(callback)


# async def add_game_handler(callback: types.CallbackQuery):
#     try:
#         teams = await read_headers(callback.message.chat.id)
#         return await choose_first_team(callback, teams)
#     except FileNotFoundError:
#         await register_state_handler(callback)

async def add_game_handler(callback: types.CallbackQuery):
    async with TournamentWorker() as worker:
        tournament = await worker.get_last_tournament(callback.message.chat.id)
        teams = await worker.get_teams(tournament.id)
        return await choose_first_team(callback, teams)


async def choose_first_team(callback, available_teams):
    await callback.message.delete()
    keyboard_button_container = types.InlineKeyboardMarkup(resize_keyboard=True)
    for team in available_teams:
        keyboard_button_container.add(types.InlineKeyboardButton(team.name, callback_data=team_callback.new(team.id)))
    await GameStorage.first_team.set()
    return await bot.send_message(callback.message.chat.id, "Оберіть першу команду",
                                  reply_markup=keyboard_button_container)


async def choose_second_team(callback: types.CallbackQuery, state: FSMContext):
    team_id = int(team_callback.parse(callback.data)['team_id'])
    async with TournamentWorker() as worker:
        team = await worker.team_repo.get(id=team_id)
        tournament = await worker.get_last_tournament(callback.message.chat.id)
        available_teams = await worker.get_teams(tournament.id)
        available_teams.remove(team)

    async with state.proxy() as data:
        data['first_team'] = team_id
    await GameStorage.next()
    keyboard_button_container = types.InlineKeyboardMarkup(resize_keyboard=True)
    for team in available_teams:
        keyboard_button_container.add(types.InlineKeyboardButton(team.name, callback_data=team_callback.new(team.id)))
    return await callback.message.edit_text("Оберіть другу команду команду", reply_markup=keyboard_button_container)



async def show_controls_buttons(callback: types.CallbackQuery, state: FSMContext):
    team_id = int(team_callback.parse(callback.data)['team_id'])
    async with state.proxy() as data:
        data['second_team'] = team_id

    await state.update_data(first_result=0)
    await state.update_data(second_result=0)
    state_data = await state.get_data()
    await GameStorage.next()

    async with TournamentWorker() as worker:
        first_team = await worker.get_team(int(state_data["first_team"]))
        second_team = await worker.get_team(int(state_data["second_team"]))

    kb = await get_controls_keyboard(first_team, second_team)


    return await callback.message.edit_text(f"{first_team.name} vs {second_team.name}"
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