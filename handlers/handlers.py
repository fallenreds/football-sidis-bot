from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import Update

from data_csv_engine import read_headers,  get_all_rows, delete_file
from handlers.utils import get_cell_color, add_or_finish_match
from maketable import get_table
from settings import bot
from buttons import DELETE_BUTTON
from workers.tournament import TournamentWorker


async def begin_match(message):
    try:
        await message.delete()
    except Exception:
        pass
    start_cmd = types.BotCommand(
        command="start", description="Меню"
    )
    add_cmd = types.BotCommand(
        command="add", description="Додати нову гру"
    )
    edit_cmd = types.BotCommand(
        command="edit", description="Редагувати гру"
    )
    exit_from_state = types.BotCommand(
        command="reload", description="Перезавантажити стан"
    )
    reload = types.BotCommand(
        command="delete", description="⚠️Видалити усі дані⚠️"
    )


    await bot.set_my_commands(
        scope=types.BotCommandScopeChat(chat_id=message.chat.id),
        commands=[start_cmd, add_cmd, edit_cmd, reload,exit_from_state]
    )
    await add_or_finish_match(message)




async def write_game_results(callback: types.CallbackQuery, state: FSMContext):
    results = await state.get_data()

    data = [
        (
            int(results.get('first_team')),
            int(results.get('first_result'))
        ),
        (
            int(results.get('second_team')),
            int(results.get('second_result'))
        ),
    ]
    async with TournamentWorker() as worker:
        tournament = await worker.get_last_tournament(callback.message.chat.id)
        await worker.add_game(tournament.id, data)

    await state.finish()

    # await add_team_results(results, callback.message.chat.id)
    return await show_statistic(callback)

async def show_statistic(callback: types.CallbackQuery):
    try:
        await callback.message.delete()
    except Exception:
        pass

    async with TournamentWorker() as worker:
        tournament = await worker.get_last_tournament(callback.message.chat.id)
        tournament_data = await worker.get_tournament_data(tournament.id)
    teams = [team for team in await worker.get_teams(tournament.id)]
    results = await calculate_all_games(tournament.id)
    # all_rows = await get_all_rows(callback.message.chat.id)
    response_text = ''
    data: dict = {}
    cell_colors = {}
    header_colors = {}

    all_rows = [[team.name for team in teams], *tournament_data]

    data['№'] = [i for i in range(1, len(all_rows))]
    for index, team in enumerate(teams):
        header_colors[index+1] = get_cell_color(team.name)
        data[team.name[1:]] = [column[index] for column in all_rows[1:]]

    first_team_color = get_cell_color(teams[0].name)
    second_team_color = get_cell_color(teams[1].name)
    third_team_color = get_cell_color(teams[2].name)

    cell_colors[(len(all_rows)-1,1)]=first_team_color
    cell_colors[(len(all_rows),1)] = first_team_color
    cell_colors[(len(all_rows) + 1,1)]= first_team_color
    cell_colors[(len(all_rows) + 2,1)] = first_team_color
    cell_colors[(len(all_rows) + 3,1)] = first_team_color

    cell_colors[(len(all_rows) - 1, 2)] = second_team_color
    cell_colors[(len(all_rows), 2)] = second_team_color
    cell_colors[(len(all_rows) + 1, 2)] = second_team_color
    cell_colors[(len(all_rows) + 2, 2)] = second_team_color
    cell_colors[(len(all_rows) + 3, 2)] = second_team_color

    cell_colors[(len(all_rows) - 1, 3)] = third_team_color
    cell_colors[(len(all_rows), 3)] = third_team_color
    cell_colors[(len(all_rows) + 1, 3)] = third_team_color
    cell_colors[(len(all_rows) + 2, 3)] = third_team_color
    cell_colors[(len(all_rows) + 3, 3)] = third_team_color

    data['№'].extend(["Матчів","Перемога","Нічия","Поразка", "Очок"])
    for result, team in zip(results, teams):
        data[team.name[1:]].extend([
                                    str(int(result['wins'])+int(result['lose'])+int(result['draw'])),
                                    result['wins'],
                                    result['draw'],
                                    result['lose'],
                                    result['points']
        ])

    image = get_table(data, cell_colors, header_colors, "#49b3a9")



    for result, team in zip(results, teams):
        response_text +=f"\n\n<b>{team.name} - балів {result['points']}</b>\n" \
                        f"всього ігор: {int(result['wins'])+int(result['lose'])+int(result['draw'])}\n" \
                        f"перемоги: {result['wins']}\n" \
                        f"поразки: {result['lose']}\n" \
                        f"нічиї {result['draw']}\n"

    kb = types.InlineKeyboardMarkup()
    kb.add(DELETE_BUTTON)
    await bot.send_photo(chat_id=callback.message.chat.id, caption=response_text, photo=image, reply_markup=kb)
    return await add_or_finish_match(callback.message)


async def calculate_all_games(tournament_id: int):
    async with TournamentWorker() as worker:
        teams = await worker.get_teams(tournament_id=tournament_id)
        result = await worker.get_result(tournament_id)
        statistic = []

        for i, team in enumerate(teams):
            team_stat = {'wins': 0, 'lose': 0, 'draw': 0, 'points': 0}
            for variant in result:
                if variant[i] == 'Победил':
                    team_stat['wins'] += 1
                    team_stat['points'] += 3
                if variant[i] == 'Проиграл':
                    team_stat['lose'] += 1
                if variant[i] == 'Ничья':
                    team_stat['draw'] += 1
                    team_stat['points'] += 1
            statistic.append(team_stat)
        return statistic


async def delete_message_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()

async def exit_from_state(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await callback.message.delete()
    return await add_or_finish_match(callback.message)

async def reload(message:types.Message, state:FSMContext):
    await message.delete()
    await state.finish()
    kb = types.InlineKeyboardMarkup()
    kb.add(
        DELETE_BUTTON
    )
    await message.answer("Успішний вихід зі станів", reply_markup=kb)

async def delete_handlers(message:types.Message, state:FSMContext):
    if state:
        await state.finish()
        await delete_file(message.chat.id)
    try:
        await message.delete()
    except Exception:
        pass
    await add_or_finish_match(message)


async def error_handler(update: Update, exception, state: FSMContext = None):
    if state:
        await state.finish()
    if update.callback_query:
        await update.callback_query.message.delete()
        user = update.callback_query.from_user
    elif update.message or update.edited_message:
        try:
            await update.message.delete()
        except Exception:
            pass
        user = update.message.from_user
    elif update.inline_query:
        user = update.inline_query.from_user

    await update.bot.send_message(
        chat_id=user.id, text=f"Сталася помилка, неможливо виконати операцію.\n{exception}"
    )
    return True

