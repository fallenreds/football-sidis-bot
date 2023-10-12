from aiogram import filters, types
from settings import ADMINS


class AdminFilter(filters.Filter):
    async def check(self, message: types.Message) -> bool:
        return is_admin(message.chat.id)


def is_admin(chat_id):
    return str(chat_id) in ADMINS
