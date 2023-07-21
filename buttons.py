from aiogram import types
DELETE_BUTTON = types.InlineKeyboardButton(
            "❌",
            callback_data="delete_message"
        )

EXIT_FROM_STATE = types.InlineKeyboardButton(
            "❌",
            callback_data="exit_from_state"
        )