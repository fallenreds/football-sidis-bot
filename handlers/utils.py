from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import MessageToDeleteNotFound

from workers.tournament import TournamentWorker
from buttons import EXIT_FROM_STATE, DELETE_BUTTON
from callbacks import *
from data_csv_engine import is_registered
from settings import bot, ADMINS
from workers.tournament import Team


async def get_controls_keyboard(first_team: Team, second_team: Team):
    """
    :return:
    """
    kb = types.InlineKeyboardMarkup()

    minus_buttons = [
        types.InlineKeyboardButton(
            f"{first_team.name}(-1)",
            callback_data=minus_team_score.new("first_result")

        ),
        types.InlineKeyboardButton(
            f"{second_team.name}(-1)",
            callback_data=minus_team_score.new("second_result")
        )

    ]
    plus_buttons = [
        types.InlineKeyboardButton(
            f"{first_team.name}(+1)",
            callback_data=plus_team_score.new("first_result")
        ),
        types.InlineKeyboardButton(
            f"{second_team.name}(+1)",
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

    async with TournamentWorker() as worker:
        first_team = await worker.get_team(int(state_data["first_team"]))
        second_team = await worker.get_team(int(state_data["second_team"]))

    kb = await get_controls_keyboard(first_team, second_team)

    if can_edit_message:
        return await callback.message.edit_text(f"{first_team.name} vs {second_team.name}"
                                                f"({state_data['first_result']}:{state_data['second_result']})",
                                                reply_markup=kb)


def set_delimiter(delimiter: str, data: list):
    return f"{delimiter.join(data)}"


async def add_or_finish_match(message):
    text = 'Вітаю. Оберіть потрібний варіант. У вас вже зареєстрований 1 матч'
    keyboard_button_container = types.InlineKeyboardMarkup(resize_keyboard=True)
    async with TournamentWorker() as worker:
        is_registered_tournament = await worker.is_registered_tournament(message.chat.id)

    if is_registered_tournament:
        keyboard_button_container.add(types.InlineKeyboardButton("Додати гру ➕", callback_data='add_game'))
        keyboard_button_container.add(types.InlineKeyboardButton("Отримати статистику ℹ️", callback_data='get_stat'))
    else:
        text = "Вітаю, у вас ще не зареєстровано жодного матчу.\n" \
               "Натисніть на кнопку нижче щоб його створити"

    keyboard_button_container.add(types.InlineKeyboardButton("Новий матч 🆕", callback_data='begin_match'))
    keyboard_button_container.add(DELETE_BUTTON)
    return await bot.send_message(message.chat.id, text, reply_markup=keyboard_button_container)


async def delete_message(chat_id, message_id):
    try:
        await bot.delete_message(chat_id, message_id)
    except Exception as error:
        pass


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


async def send_multiple_messages(ids: list, text: str, reply_markup):
    for _id in ids:
        await bot.send_message(int(_id), text=text, reply_markup=reply_markup)



