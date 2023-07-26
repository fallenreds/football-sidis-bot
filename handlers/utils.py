from aiogram import types
from aiogram.dispatcher import FSMContext

from buttons import EXIT_FROM_STATE, DELETE_BUTTON
from callbacks import *
from data_csv_engine import is_registered
from settings import bot


async def get_controls_keyboard(state: FSMContext):
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
    kb.add(EXIT_FROM_STATE)
    return kb


async def get_controls_answer(callback: types.CallbackQuery, state: FSMContext):
    can_edit_message = False
    state_data = await state.get_data()
    if callback.data.startswith(plus_team_score.prefix):
        team_key = plus_team_score.parse(callback.data)['team_key']
        async with state.proxy() as data:
            data[team_key] = int(state_data[team_key]) + 1
            can_edit_message = True

    if callback.data.startswith(minus_team_score.prefix):
        team_key = minus_team_score.parse(callback.data)['team_key']
        async with state.proxy() as data:
            if int(state_data[team_key]) > 0:
                data[team_key] = int(state_data[team_key]) - 1
                can_edit_message = True

    state_data = await state.get_data()
    kb = await get_controls_keyboard(state)
    if can_edit_message:
        return await callback.message.edit_text(f"{state_data['first_team']} vs {state_data['second_team']}"
                                                f"({state_data['first_result']}:{state_data['second_result']})",
                                                reply_markup=kb)


def set_delimiter(delimiter: str, data: list):
    return f"{delimiter.join(data)}"


async def add_or_finish_match(message):
    text = 'Вітаю. Оберіть потрібний варіант. У вас вже зареєстрований 1 матч'
    keyboard_button_container = types.InlineKeyboardMarkup(resize_keyboard=True)
    if await is_registered(message.chat.id):
        keyboard_button_container.add(types.InlineKeyboardButton("Додати гру ➕", callback_data='add_game'))
        keyboard_button_container.add(types.InlineKeyboardButton("Отримати статистику ℹ️", callback_data='get_stat'))
    else:
        text = "Вітаю, у вас ще не зареєстровано жодного матчу.\n" \
               "Натисніть на кнопку нижче щоб його створити"
    keyboard_button_container.add(types.InlineKeyboardButton("Новий матч 🆕", callback_data='begin_match'))
    keyboard_button_container.add(DELETE_BUTTON)
    return await bot.send_message(message.chat.id, text, reply_markup=keyboard_button_container)


def get_cell_color(text):
    smile = text[0]
    if smile == "🔵":
        return "#4785e8"
    if smile == "🟡":
        return "#feff02"
    if smile == "🟠":
        return "#fe9900"
    if smile == "⚪":
        return "white"
    if smile == "🔴":
        return "#fb5c5f"
    if smile == "🟢":
        return "#4adc42"
