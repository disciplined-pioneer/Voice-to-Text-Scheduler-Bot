import re

from aiogram.types import Message
from aiogram.filters import Command
from aiogram import F, types, Router
from aiogram.fsm.context import FSMContext

from db.psql.models.models import SessionFactory, UserAlerts
from bot.templates.user.menu import platform_button, alerts_cancellation_button
from bot.templates.user.setting_notifications_temp import (
    notification_text, NotificationState, invalid_time_format_message
)


router = Router()
session = SessionFactory()

# Обработчик для команды настройки уведомлений
@router.message(Command("notifications"))
@router.message(F.text == "🔔 Настроить уведомления")
async def notification_processing(msg: Message, state: FSMContext):

    # Переходим в состояние ожидания ввода времени
    await msg.reply(notification_text,
                     reply_markup=alerts_cancellation_button,
                     parse_mode='HTML')
    
    await state.set_state(NotificationState.waiting_for_time)


# Обработчик для состояния ожидания времени
@router.message(NotificationState.waiting_for_time)
async def process_time(msg: Message, state: FSMContext):

    await msg.chat.delete_message(message_id=msg.message_id - 1)

    if msg.text == "❌ Отменить настройку":
        await cancel_recording(msg, state)
        return

    # Регулярное выражение для извлечения чисел и временных единиц (минут и часов)
    user_input = msg.text.strip().lower()
    time_pattern = r'(\d+)\s*(час|мин|ч|м)\s*(\d+)?\s*(мин|м)?'
    
    # Смотрим, подходит ли ввод под наш паттерн
    match = re.match(time_pattern, user_input)

    if match:
        hours = 0
        minutes = 0

        # Обрабатываем часы
        if match.group(2) in ["час", "ч"]:
            hours = int(match.group(1))
        
        # Обрабатываем минуты
        if match.group(4) in ["мин", "м"]:
            minutes = int(match.group(3) if match.group(3) else 0)
        elif match.group(2) in ["мин", "м"]:
            minutes = int(match.group(1))

        # Изменяем алерт в БД
        tg_id = msg.from_user.id
        total_minutes = (hours * 60) + minutes

        session.merge(UserAlerts(tg_id=tg_id, alerts=total_minutes))
        session.commit()
        session.close()

        await msg.answer(f"✅ Вы выбрали {total_minutes} минут(ы). Уведомление установлено! 😉",
                         reply_markup=platform_button)
        await state.clear()
    else:
        await msg.answer(invalid_time_format_message,
                         reply_markup=alerts_cancellation_button,)


# Обработчик кнопки "❌ Отменить настройку"
@router.message(lambda message: message.text == "❌ Отменить настройку")
async def cancel_recording(message: types.Message, state: FSMContext):
    current_state = await state.get_state()

    # Если мы находимся в нужном состоянии (ожидание ввода времени)
    if current_state == NotificationState.waiting_for_time:

        await message.chat.delete_message(message_id=message.message_id - 1)

        # Отменяем состояние и возвращаем в главное меню
        await state.clear()
        await message.answer("Вы отменили настройку и вернулись в главное меню ☺️",
                             reply_markup=platform_button)
