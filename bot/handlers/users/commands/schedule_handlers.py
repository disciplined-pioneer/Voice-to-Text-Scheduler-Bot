from datetime import datetime, timedelta

from aiogram.types import Message
from aiogram.filters import Command
from aiogram import F, types, Router
from aiogram.fsm.context import FSMContext

from db.psql.models.models import SessionFactory, Event
from core.voice_processor import generate_event_message
from bot.templates.user.menu import schedule_keyboard, platform_button

router = Router()

@router.message(Command("records"))
@router.message(F.text == '📜 Посмотреть записи')
async def voice_recording(msg: Message, state: FSMContext):
    await msg.answer('Пожалуйста, выберите подходящий период 🙂', reply_markup=schedule_keyboard)


@router.message(lambda message: message.text in ["📅 На сегодня", "📆 На завтра", "🗓️ На неделю", "📖 На месяц"])
async def schedule_handler(message: types.Message):

    # Создаем сессию для работы с базой данных
    session = SessionFactory()

    text = message.text
    user_id = message.from_user.id

    # Формирование фильтра даты в зависимости от выбранной кнопки
    if text == "📅 На сегодня":
        date_filter = datetime.today().date()
    elif text == "📆 На завтра":
        date_filter = (datetime.today() + timedelta(days=1)).date()
    elif text == "🗓️ На неделю":
        date_filter = None
    elif text == "📖 На месяц":
        date_filter = None

    # Фильтрация событий по tg_id пользователя и по дате
    if date_filter:
        events = session.query(Event).filter(Event.tg_id == user_id, Event.date == date_filter).all()
    else:
        events = session.query(Event).filter(Event.tg_id == user_id).all()

    # Преобразуем события в форматированный текст
    if events:
        events_list = [event.__dict__ for event in events]
        event_message = generate_event_message(events_list, message=f"<b><u>В заданный период у вас следующие задачи:</u></b>\n\n")  # Используем функцию для создания сообщения
    else:
        event_message = "У вас нет событий за выбранный период! 🙅‍♂️"

    # Отправляем сообщение с расписанием и кнопками
    await message.reply(event_message,
                         reply_markup=schedule_keyboard,
                         parse_mode='HTML')


@router.message(F.text == '◀️ Назад')
async def voice_recording(msg: Message, state: FSMContext):

    await msg.answer('Вы вернулись в главное меню 😊', reply_markup=platform_button)