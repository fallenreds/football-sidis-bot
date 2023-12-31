import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, executor, filters, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

load_dotenv()

# BOT_SETTINGS
BOT_TOKEN = os.getenv('BOT_TOKEN')
PARSE_MODE = "HTML"
ADMINS = os.environ.get("ADMINS").split(',')
storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN, parse_mode=PARSE_MODE)
dp = Dispatcher(bot, storage=storage,)

# CSV SETTINGS



AVAILABLE_COLORS = [
    "🔵",
    "🟡",
    "🟠",
    "🟢",
    "⚪️",
    "🔴",
]


COLORS = [
    'blue',
    "yellow",
    "orange",
    "white",
    "red",
    "green",

]

db_url = "sqlite+aiosqlite:///db.sqlite3"
MATCHES_PATH = 'matches/'