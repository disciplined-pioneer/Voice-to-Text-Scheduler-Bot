import asyncio
from config import TOKEN

from aiogram import Bot, Dispatcher
from core.notification_scheduler import NotificationScheduler

from db.psql.models.models import SessionFactory
from bot.handlers.users.commands.start import router as hello_router
from bot.handlers.users.commands.voice_recording import router as voice_router
from bot.handlers.users.commands.schedule_handlers import router as schedule_router
from bot.handlers.users.commands.setting_notifications import router as notifications_router

# Создание экземпляра бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Асинхронная функция для запуска бота и планировщика
async def main():
    notification_scheduler = NotificationScheduler(bot, SessionFactory)
    notification_scheduler.start() # Запуск планировщика уведомлений

    dp.include_router(hello_router)  # Включаем роутер для приветствия 
    dp.include_router(voice_router)  # Включаем роутер для обработки голосовых сообщений
    dp.include_router(schedule_router)  # Включаем роутер для обработки вывода данных
    dp.include_router(notifications_router)  # Включаем роутер для настройки уведомлений

    await dp.start_polling(bot)  # Запуск Telegram-бота

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        text = 'Бот был Вами остановлен 🛑'
        print('-' * len(text))
        print(f'{text}')
        print('-' * len(text))
