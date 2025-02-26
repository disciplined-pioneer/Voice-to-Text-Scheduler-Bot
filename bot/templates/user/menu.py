from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

platform_button = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📜 Посмотреть записи")],
        [KeyboardButton(text="➕ Добавить запись")],
        [KeyboardButton(text="🔔 Настроить уведомления")],
    ],
    resize_keyboard=True,  # Кнопки адаптируются под размер экрана
)
