import asyncio
import logging

from aiogram import Bot, Dispatcher, executor, filters, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from sqlalchemy.ext.asyncio import create_async_engine

import register_handlers
from settings import *
from db.models import Base


async def on_startup(_):
    engine = create_async_engine(db_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == '__main__':
    register_handlers.handler_register(dp)
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
