import asyncio
from config import TOKEN
from aiogram import Bot, Dispatcher  

from bot.handlers.users.commands.start import router as hello_router # Роутер для приветствия
from bot.handlers.users.commands.voice_recording import router as voice_router # Роутер для обработки голосовых сообщений
from bot.handlers.users.commands.schedule_handlers import router as schedule_router # Роутер для обработки вывода данных

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def main():

    dp.include_router(hello_router)  # Включаем роутер для приветствия 
    dp.include_router(voice_router)  # Включаем роутер для обработки голосовых сообщений
    dp.include_router(schedule_router)  # Включаем роутер для обработки вывода данных

    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        text = 'Бот был Вами остановлен 🛑'
        print('-' * len(text))
        print(f'{text}')
        print('-' * len(text))