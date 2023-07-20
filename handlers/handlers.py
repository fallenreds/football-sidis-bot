from aiogram import types
from aiogram.utils.callback_data import CallbackData
from aiogram.dispatcher import FSMContext
from aiogram import Dispatcher

from buttons import DELETE_BUTTON
from handlers.utils import get_controls_keyboard, set_delimiter, get_controls_answer
from settings import bot, AVAILABLE_COLORS
from states import RegisterTeamsStorage, GameStorage
from data_csv_engine import register_teams, read_headers, add_team_results, calculate_all_games, get_all_rows, \
    edit_team_results

from callbacks import *


async def begin_match(message):
    try:
        await message.delete()
    except Exception:
        pass
    start_cmd = types.BotCommand(
        command="start", description="Почати"
    )
    add_cmd = types.BotCommand(
        command="add", description="Додати"
    )
    edit_cmd = types.BotCommand(
        command="edit", description="Редагувати"
    )

    await bot.set_my_commands(
        scope=types.BotCommandScopeChat(chat_id=message.chat.id),
        commands=[start_cmd, add_cmd, edit_cmd]
    )
    keyboard_button_container = types.InlineKeyboardMarkup(resize_keyboard=True)
    keyboard_button_container.add(
        types.InlineKeyboardButton("Почати гру⚽️", callback_data='begin_match')
    )
    return await bot.send_message(message.chat.id, 'Чудово. Тепер ви можете почати гру',
                                  reply_markup=keyboard_button_container)


async def register_state_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()



    await RegisterTeamsStorage.first.set()
    kb = types.InlineKeyboardMarkup()
    for color in AVAILABLE_COLORS:
        kb.add(
            types.InlineKeyboardButton(
                color,
                callback_data=team_color.new(color)
            )
        )
    await bot.send_message(callback.message.chat.id,
                           text="Cпочатку оберіть колір команди, а потім введіть її назву",
                           reply_markup=kb
                           )



async def register_first_color(callback: types.CallbackQuery,
                               state:FSMContext):
    await callback.message.delete()
    text = "Введіть назву першої команди"
    bot_message = await bot.send_message(callback.message.chat.id, text)
    first_color = team_color.parse(callback.data)['color']
    await state.update_data(first_color=first_color)
    await state.update_data(prevent_message=bot_message)



async def register_first_team(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    if not state_data.get('first_color'):
        return
    await state_data['prevent_message'].delete()
    await message.delete()
    async with state.proxy() as data:
        data['first'] = f"{state_data['first_color']}{message.text}"
    await RegisterTeamsStorage.next()

    kb = types.InlineKeyboardMarkup()
    colors = [color for color in AVAILABLE_COLORS]
    colors.remove(state_data['first_color'])
    for color in colors:
        kb.add(
            types.InlineKeyboardButton(
                color,
                callback_data=team_color.new(color)
            )
        )
    await bot.send_message(message.chat.id,
                           f"Чудово, я запам'ятав <b>{state_data['first_color']}{message.text}</b>. Тепер оберіть колір другої команди",
                           reply_markup=kb)


async def register_second_color(callback: types.CallbackQuery,
                               state:FSMContext):
    await callback.message.delete()
    text = "Введіть назву другої команди"
    bot_message = await bot.send_message(callback.message.chat.id, text)
    first_color = team_color.parse(callback.data)['color']
    await state.update_data(second_color=first_color)
    await state.update_data(prevent_message=bot_message)

async def register_second_team(message: types.Message, state: FSMContext):
    await message.delete()
    state_data = await state.get_data()
    if not state_data.get('second_color'):
        return
    await state_data['prevent_message'].delete()

    async with state.proxy() as data:
        data['second'] = f"{state_data['second_color']}{message.text}"
    await RegisterTeamsStorage.next()
    kb = types.InlineKeyboardMarkup()

    colors = [color for color in AVAILABLE_COLORS]
    colors.remove(state_data['second_color'])

    for color in colors:
        kb.add(
            types.InlineKeyboardButton(
                color,
                callback_data=team_color.new(color)
            )
        )
    await bot.send_message(message.chat.id,
                           f"Оберіть колір останньої команди",
                           reply_markup=kb
                           )

async def register_third_color(callback: types.CallbackQuery,
                               state:FSMContext):
    await callback.message.delete()
    text = "Супер, уведіть назву останної команди"
    bot_message = await bot.send_message(callback.message.chat.id, text)
    third_color = team_color.parse(callback.data)['color']
    await state.update_data(third_color=third_color)
    await state.update_data(prevent_message=bot_message)

async def register_third_team(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    if not state_data.get('third_color'):
        return
    await state_data['prevent_message'].delete()
    await message.delete()

    async with state.proxy() as data:
        data['third'] = f"{state_data['third_color']}{message.text}"
    state_data = await state.get_data()
    await state.finish()

    await register_teams(
                            {
                                'first': state_data['first'],
                                'second': state_data['second'],
                                'third': state_data['third']
                            }
                         )

    team_list = [state_data['first'], state_data['second'], state_data['third']]
    kb = types.InlineKeyboardMarkup()
    kb.add(DELETE_BUTTON)
    await bot.send_message(message.chat.id, f'Чудово. Я записав 3 команди:\n<b>{" ".join(team_list)}</b>', reply_markup=kb)
    return await add_or_finish_match(message)


async def add_or_finish_match(message):
    keyboard_button_container = types.InlineKeyboardMarkup(resize_keyboard=True)
    keyboard_button_container.add(types.InlineKeyboardButton("Додати гру ➕", callback_data='add_game'))
    keyboard_button_container.add(types.InlineKeyboardButton("Завершити матч 🏁", callback_data='finish_match'))
    return await bot.send_message(message.chat.id, "Оберіть одну із дій", reply_markup=keyboard_button_container)




async def add_game_command_handler(message:types.Message):
    callback = types.CallbackQuery()
    callback.message = message
    await add_game_handler(callback)




async def add_game_handler(callback: types.CallbackQuery):
    teams = await read_headers()
    return await choose_first_team(callback, teams)


async def choose_first_team(callback, available_teams):
    await callback.message.delete()
    keyboard_button_container = types.InlineKeyboardMarkup(resize_keyboard=True)
    for team in available_teams:
        keyboard_button_container.add(types.InlineKeyboardButton(team, callback_data=team_callback.new(team)))
    await GameStorage.first_team.set()
    return await bot.send_message(callback.message.chat.id, "Оберіть першу команду",
                                  reply_markup=keyboard_button_container)


async def choose_second_team(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()

    team_label = team_callback.parse(callback.data)['team_label']
    available_teams = await read_headers()
    available_teams.remove(team_label)
    async with state.proxy() as data:
        data['first_team'] = team_label
    await GameStorage.next()

    keyboard_button_container = types.InlineKeyboardMarkup(resize_keyboard=True)
    for team in available_teams:
        keyboard_button_container.add(types.InlineKeyboardButton(team, callback_data=team_callback.new(team)))
    return await bot.send_message(callback.message.chat.id, "Оберіть другу команду команду",
                                  reply_markup=keyboard_button_container)









async def show_controls_buttons(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()

    team_label = team_callback.parse(callback.data)['team_label']
    async with state.proxy() as data:
        data['second_team'] = team_label

    await state.update_data(first_result=0)
    await state.update_data(second_result=0)
    state_data = await state.get_data()
    await GameStorage.next()

    kb = await get_controls_keyboard(state)

    return await bot.send_message(callback.message.chat.id, f"{state_data['first_team']} vs {state_data['first_team']}"
                                                            f"({state_data['first_result']}:{state_data['second_result']})",
                                  reply_markup=kb)






    state_data = await state.get_data()
    kb = await get_controls_keyboard(state)
    return await bot.send_message(callback.message.chat.id, f"{state_data['first_team']} vs {state_data['second_team']}"
                                                            f"({state_data['first_result']}:{state_data['second_result']})",
                                  reply_markup=kb)


async def edit_game_results(callback:types.CallbackQuery,
                            state:FSMContext
                            ):
    await callback.message.delete()
    results = await state.get_data()
    row_number = results['edit_row_number']
    await state.finish()
    results_in_order = await edit_team_results(results,int(row_number))
    teams = await read_headers()
    response = f"{set_delimiter('-', teams)}\n{set_delimiter('-', results_in_order)}"
    kb = types.InlineKeyboardMarkup()
    kb.add(DELETE_BUTTON)
    await bot.send_message(callback.message.chat.id, response, reply_markup=kb)
    return await add_or_finish_match(callback.message)

async def write_game_results(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    results = await state.get_data()
    await state.finish()
    row_index = len(await get_all_rows())
    results_in_order = await add_team_results(results)
    teams = await read_headers()

    response = f"{set_delimiter('-', teams)}\n{row_index-1}) {set_delimiter('-', results_in_order)}"
    kb = types.InlineKeyboardMarkup()
    kb.add(DELETE_BUTTON)
    await bot.send_message(callback.message.chat.id, response, reply_markup=kb)
    return await add_or_finish_match(callback.message)


async def show_statistic(callback: types.CallbackQuery):
    await callback.message.delete()

    teams = await read_headers()
    results = await calculate_all_games()
    response_text = ''
    for data in await get_all_rows():
        response_text += f'{set_delimiter("-", data)}\n'
    response_text += "\n"
    for result, team in zip(results, teams):
        response_text += f"<b>{team}</b> - перемоги: {result['wins']}, поразки: {result['lose']}, нічиї: {result['draw']}. <b>Загальний бал:</b> {result['points']}\n"
    kb = types.InlineKeyboardMarkup()
    await bot.send_message(callback.message.chat.id, response_text, reply_markup=kb)
    return await begin_match(callback.message)
async def delete_message_handler(callback: types.CallbackQuery, state:FSMContext):
    await callback.message.delete()