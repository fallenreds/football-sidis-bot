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
from workers.tournament import TournamentWorker


async def edit_games_command_handler(message: types.Message):
    await message.delete()
    async with TournamentWorker() as worker:
        tournament = await worker.get_last_tournament(message.chat.id)
        if not tournament:
            return await add_or_finish_match(message)

        tournament_data = await worker.get_tournament_data(tournament.id)
    await EditGameStorage.first_team.set()
    kb = types.InlineKeyboardMarkup()

    for index, game in enumerate(tournament_data):
        kb.add(
            types.InlineKeyboardButton(
                f"{index + 1}--{game}",
                callback_data=edit_game_callback.new(index)
            )
        )
    kb.add(DELETE_BUTTON)
    text = "Натисніть на гру, яку хочете редагувати"
    await bot.send_message(message.chat.id, text=text, reply_markup=kb)


async def edit_game_handler(callback: types.CallbackQuery, state: FSMContext):
    row_number = edit_game_callback.parse(callback.data)['row_number']
    await state.update_data(row_number=row_number)
    async with TournamentWorker() as worker:
        tournament = await worker.get_last_tournament(callback.message.chat.id)
        teams = await worker.get_teams(tournament_id=tournament.id)
    return await choose_first_team(callback, teams)


async def choose_first_team(callback, available_teams):
    keyboard_button_container = types.InlineKeyboardMarkup(resize_keyboard=True)
    for team in available_teams:
        keyboard_button_container.add(types.InlineKeyboardButton(team.name, callback_data=team_callback.new(team.id)))
    await EditGameStorage.first_team.set()
    return await callback.message.edit_text("Оберіть першу команду", reply_markup=keyboard_button_container)


async def choose_second_team(callback: types.CallbackQuery, state: FSMContext):
    team_id = int(team_callback.parse(callback.data)['team_id'])
    async with TournamentWorker() as worker:
        tournament = await worker.get_last_tournament(callback.message.chat.id)
        teams = [team for team in await worker.get_teams(tournament_id=tournament.id)]

    for team in teams:
        if team.id == team_id:
            teams.remove(team)

    async with state.proxy() as data:
        data['first_team'] = team_id
    await EditGameStorage.next()

    keyboard_button_container = types.InlineKeyboardMarkup(resize_keyboard=True)
    for team in teams:
        keyboard_button_container.add(types.InlineKeyboardButton(team.name, callback_data=team_callback.new(team.id)))
    return await callback.message.edit_text("Оберіть другу команду команду", reply_markup=keyboard_button_container)


async def show_controls_buttons(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        team_id = team_callback.parse(callback.data)['team_id']
        data['second_team'] = team_id

    await state.update_data(first_result=0)
    await state.update_data(second_result=0)
    state_data = await state.get_data()
    await EditGameStorage.next()

    async with TournamentWorker() as worker:
        first_team = await worker.get_team(int(state_data["first_team"]))
        second_team = await worker.get_team(int(state_data["second_team"]))
    kb = await get_controls_keyboard(first_team, second_team)

    return await callback.message.edit_text(f"{first_team.name} vs {second_team.name}"
                                            f"({state_data['first_result']}:{state_data['second_result']})",
                                            reply_markup=kb)


async def edit_game_results(callback: types.CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    row_number = int(state_data['row_number'])
    async with TournamentWorker() as worker:
        tournament = await worker.get_last_tournament(callback.message.chat.id)
        games = [game for game in await worker.game_repo.list(tournament_id=tournament.id)]
        game = games[row_number]
        data = [
            (
                int(state_data["first_team"]),
                int(state_data["first_result"])
            ),
            (
                int(state_data["second_team"]),
                int(state_data["second_result"])
            )
        ]
        await worker.edit_game(game.id, data)
    await state.finish()
    await callback.message.delete()
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
