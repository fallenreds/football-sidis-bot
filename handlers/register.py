from aiogram import Dispatcher
from aiogram import types
from aiogram.dispatcher import FSMContext

from buttons import DELETE_BUTTON
from callbacks import *
from data_csv_engine import register_teams
from handlers.utils import add_or_finish_match
from settings import bot, AVAILABLE_COLORS
from states import RegisterTeamsStorage


async def register_state_handler(callback: types.CallbackQuery, state: FSMContext=None):
    try:
        await callback.message.delete()
    except Exception:
        pass

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
                               state: FSMContext):
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
                                state: FSMContext):
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
    colors.remove(state_data['first_color'])
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
                               state: FSMContext):
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
        },
        message.chat.id
    )

    team_list = [state_data['first'], state_data['second'], state_data['third']]
    kb = types.InlineKeyboardMarkup()
    kb.add(DELETE_BUTTON)
    await bot.send_message(message.chat.id, f'Чудово. Я записав 3 команди:\n<b>{" ".join(team_list)}</b>',
                           reply_markup=kb)
    return await add_or_finish_match(message)

def register_register_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(register_state_handler, lambda c: c.data == 'begin_match')

    dp.register_callback_query_handler(register_first_color, lambda c: c.data.startswith(team_color.prefix),
                                       state=RegisterTeamsStorage.first)
    dp.register_callback_query_handler(register_second_color, lambda c: c.data.startswith(team_color.prefix),
                                       state=RegisterTeamsStorage.second)
    dp.register_callback_query_handler(register_third_color, lambda c: c.data.startswith(team_color.prefix),
                                       state=RegisterTeamsStorage.third)

    dp.register_message_handler(register_first_team, state=RegisterTeamsStorage.first)
    dp.register_message_handler(register_second_team, state=RegisterTeamsStorage.second)
    dp.register_message_handler(register_third_team, state=RegisterTeamsStorage.third)