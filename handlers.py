from aiogram import types
from aiogram.utils.callback_data import CallbackData
from aiogram.dispatcher import FSMContext
from settings import bot
from states import RegisterTeamsStorage, GameStorage
from data_csv_engine import register_teams, read_headers, add_team_results,calculate_all_games,get_all_rows


team_callback = CallbackData('team', 'team_label')
team_goal_callback = CallbackData('team_goal', 'result')

async def begin_match(message):
    keyboard_button_container = types.InlineKeyboardMarkup(resize_keyboard=True)
    keyboard_button_container.add(
        types.InlineKeyboardButton("Почати гру⚽️", callback_data='begin_match')
    )
    return await bot.send_message(message.chat.id, 'Чудово. Тепер ви можете почати гру',
                                  reply_markup=keyboard_button_container)


async def register_state_handler(callback: types.CallbackQuery):
    await bot.send_message(callback.message.chat.id, text="Введіть назви команд (3 команди)")
    await bot.send_message(callback.message.chat.id, text="Очікую назву першої команди")
    await RegisterTeamsStorage.first.set()


async def register_first_team(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['first'] = message.text

    await RegisterTeamsStorage.next()
    await bot.send_message(message.chat.id,
                           f"Чудово, я запам'ятав <b>{message.text}</b>. Тепер уведіть назву наступної команди")


async def register_second_team(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['second'] = message.text
    await RegisterTeamsStorage.next()
    await bot.send_message(message.chat.id, f"Супер, уведіть назву останної команди")


async def register_third_team(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['third'] = message.text

    teams_labels_data = await state.get_data()
    await state.finish()

    await register_teams(teams_labels_data)
    team_list = list(teams_labels_data.values())
    await bot.send_message(message.chat.id, f'Чудово. Я записав 3 команди: <b>{" ".join(team_list)}</b>')
    return await add_or_finish_match(message)


async def add_or_finish_match(message):
    keyboard_button_container = types.InlineKeyboardMarkup(resize_keyboard=True)
    keyboard_button_container.add(types.InlineKeyboardButton("Додати гру ➕", callback_data='add_game'))
    keyboard_button_container.add(types.InlineKeyboardButton("Завершити матч 🏁", callback_data='finish_match'))
    return await bot.send_message(message.chat.id, "Оберіть одну із дій", reply_markup=keyboard_button_container)


async def add_game_handler(callback: types.CallbackQuery):
    teams = await read_headers()
    return await choose_first_team(callback, teams)




async def choose_first_team(callback, available_teams):
    keyboard_button_container = types.InlineKeyboardMarkup(resize_keyboard=True)
    for team in available_teams:
        keyboard_button_container.add(types.InlineKeyboardButton(team, callback_data=team_callback.new(team)))
    await GameStorage.first_team.set()
    return await bot.send_message(callback.message.chat.id, "Оберіть першу команду", reply_markup=keyboard_button_container)



async def choose_second_team(callback: types.CallbackQuery, state:FSMContext):
    team_label = team_callback.parse(callback.data)['team_label']
    available_teams = await read_headers()
    available_teams.remove(team_label)
    async with state.proxy() as data:
        data['first_team'] = team_label
    await GameStorage.next()

    keyboard_button_container = types.InlineKeyboardMarkup(resize_keyboard=True)
    for team in available_teams:
        keyboard_button_container.add(types.InlineKeyboardButton(team, callback_data=team_callback.new(team)))
    return await bot.send_message(callback.message.chat.id, "Оберіть другу команду команду",reply_markup=keyboard_button_container)

async def get_first_team_result(callback: types.CallbackQuery, state:FSMContext):
    team_label = team_callback.parse(callback.data)['team_label']
    async with state.proxy() as data:
        data['second_team'] = team_label
    await GameStorage.next()
    return await bot.send_message(callback.message.chat.id, "Напишіть результат першої команди")


async def get_second_team_result(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['first_result'] = message.text
    await GameStorage.next()
    return await bot.send_message(message.chat.id, "Напишіть результат другої команди")



def set_delimiter(delimiter:str, data:list):
    return f"{delimiter.join(data)}"

async def write_game_results(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['second_result'] = message.text
    results = await state.get_data()
    await state.finish()
    results_in_order = await add_team_results(results)
    teams = await read_headers()
    response = f"{set_delimiter('-', teams)}\n{set_delimiter('-', results_in_order)}"

    await bot.send_message(message.chat.id, response)
    return await add_or_finish_match(message)


async def show_statistic(callback: types.CallbackQuery):
    teams = await read_headers()
    results = await calculate_all_games()
    response_text=''
    for data in await get_all_rows():
        response_text+=f'{set_delimiter("-", data)}\n'
    response_text+="\n"
    for result, team in zip(results, teams):
        response_text+=f"<b>{team}</b> - перемоги: {result['wins']}, поразки: {result['lose']}, нічиї: {result['draw']}. <b>Загальний бал:</b> {result['points']}\n"
    await bot.send_message(callback.message.chat.id, response_text)
    return await begin_match(callback.message)





















