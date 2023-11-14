from aiogram.utils import executor
from InstanceBot import dp
import handlers
import database

async def on_startup(dp):
    database.db.check_db()
    print('Бот запущен')

    handlers.hand_user.hand_add(dp)
    handlers.hand_admin.hand_add(dp)

executor.start_polling(dp, skip_updates=True, on_startup=on_startup)