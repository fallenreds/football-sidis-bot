from aiogram import types
from aiogram.dispatcher import FSMContext
from data_csv_engine import read_headers, add_team_results, calculate_all_games, get_all_rows, delete_file
from handlers.utils import get_cell_color, add_or_finish_match
from maketable import get_table
from settings import bot
from buttons import DELETE_BUTTON

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
    reload = types.BotCommand(
        command="reload", description="⚠️Видалити усі дані⚠️"
    )

    await bot.set_my_commands(
        scope=types.BotCommandScopeChat(chat_id=message.chat.id),
        commands=[start_cmd, add_cmd, edit_cmd, reload]
    )
    await add_or_finish_match(message)




async def write_game_results(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    results = await state.get_data()
    await state.finish()
    await add_team_results(results, callback.message.chat.id)
    return await show_statistic(callback)

async def show_statistic(callback: types.CallbackQuery):
    try:
        await callback.message.delete()
    except Exception:
        pass
    teams = await read_headers(callback.message.chat.id)
    results = await calculate_all_games(callback.message.chat.id)
    all_rows = await get_all_rows(callback.message.chat.id)
    response_text = ''
    data:dict={}
    cell_colors = {}
    header_colors = {}
    data['№']=[i for i in range(1, len(all_rows))]
    for index, team in enumerate(teams):
        header_colors[index+1] = get_cell_color(team)
        data[team[1:]]=[column[index] for column in all_rows[1:]]

    first_team_color = get_cell_color(teams[0])
    second_team_color = get_cell_color(teams[1])
    third_team_color = get_cell_color(teams[2])

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
        data[team[1:]].extend([
                                    str(int(result['wins'])+int(result['lose'])+int(result['draw'])),
                                    result['wins'],
                                    result['draw'],
                                    result['lose'],
                                    result['points']
        ])

    image = get_table(data, cell_colors, header_colors, "#49b3a9")



    for result, team in zip(results, teams):
        response_text +=f"\n\n<b>{team} - балів {result['points']}</b>\n" \
                        f"всього ігор: {int(result['wins'])+int(result['lose'])+int(result['draw'])}\n" \
                        f"перемоги: {result['wins']}\n" \
                        f"поразки: {result['lose']}\n" \
                        f"нічиї {result['draw']}\n"

    kb = types.InlineKeyboardMarkup()
    kb.add(DELETE_BUTTON)
    await bot.send_photo(chat_id=callback.message.chat.id, caption=response_text, photo=image, reply_markup=kb)
    return await add_or_finish_match(callback.message)



async def delete_message_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()

async def exit_from_state(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await callback.message.delete()
    return await add_or_finish_match(callback.message)

async def reload(message:types.Message, state:FSMContext):
    if state:
        await state.finish()
        await delete_file(message.chat.id)
    try:
        await message.delete()
    except Exception:
        pass
    await add_or_finish_match(message)