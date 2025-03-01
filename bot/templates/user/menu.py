from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

platform_button = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📜 Посмотреть записи")],
        [KeyboardButton(text="➕ Добавить запись")],
        [KeyboardButton(text="🔔 Настроить уведомления")],
    ],
    resize_keyboard=True,
)

schedule_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📅 На сегодня"), KeyboardButton(text="📆 На завтра")],
        [KeyboardButton(text="🗓️ На неделю"), KeyboardButton(text="📖 На месяц")],
        [KeyboardButton(text="◀️ Назад")]
    ],
    resize_keyboard=True,
)

voice_cancellation_button = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="❌ Отменить запись")]
    ],
    resize_keyboard=True,
)


voice_confirmation_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✅ Добавить мероприятия", callback_data="add_events")],
        [InlineKeyboardButton(text="❌ Отменить мероприятия", callback_data="cancel_events")]
    ]
)

alerts_cancellation_button = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="❌ Отменить настройку")]
    ],
    resize_keyboard=True,
)