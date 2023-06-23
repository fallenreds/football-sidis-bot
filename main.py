from aiogram import Bot, Dispatcher, executor, filters, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import register_handlers
from settings import *


if __name__ == '__main__':
    register_handlers.handler_register(dp)
    executor.start_polling(dp, skip_updates=True)

