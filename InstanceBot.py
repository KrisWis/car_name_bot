from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from Config import BOT_TOKEN, YOOMONEY_TOKEN
from yoomoney import Client

storage = MemoryStorage()

bot = Bot(token=BOT_TOKEN, parse_mode='HTML')
dp = Dispatcher(bot, storage=storage)

yoomoney_token = YOOMONEY_TOKEN
yoomoney_client = Client(yoomoney_token)
