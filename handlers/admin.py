from aiogram.types import *
from repository.repositories import ChatRepository
from settings import db_url
from aiogram import Dispatcher
from filters import AdminFilter
async def user_statistic_handler(message:Message):
    await message.delete()
    repository = ChatRepository(db_url)
    chats = await repository.list()

    await message.answer(
        text=f"Наразі бот використовується в {len(chats.all())} чатах."
    )


def register_admin_handlers(dp:Dispatcher):

    dp.register_message_handler(
        user_statistic_handler,
        AdminFilter(),
        commands='statistic',
        state=['*']
    )