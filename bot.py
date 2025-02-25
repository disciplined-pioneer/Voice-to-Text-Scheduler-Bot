import asyncio
from config import TOKEN
from aiogram import Bot, Dispatcher  

from bot.handlers.users.commands.start import router as hello_router # Роутер для приветствия

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def main():

    dp.include_router(hello_router)  # Включаем роутер для приветствия 

    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        text = 'Бот был Вами остановлен 🛑'
        print('-' * len(text))
        print(f'{text}')
        print('-' * len(text))