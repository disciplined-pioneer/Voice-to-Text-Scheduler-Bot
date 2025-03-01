
from aiogram.types import Message
from aiogram.filters import Command
from aiogram import F, types, Router
from aiogram.fsm.context import FSMContext

from core.voice_processor import VoiceProcessor

from db.psql.models.models import SessionFactory, Event, UserAlerts
from bot.templates.user.menu import voice_cancellation_button, platform_button
from bot.templates.user.voice_recording_temp import *


router = Router()
session = SessionFactory()

# Команда /voice
@router.message(Command("voice_recording"))
@router.message(F.text == '➕ Добавить запись')
async def voice_recording(msg: Message, state: FSMContext):

    await msg.reply(voice_instruction_message,
                    reply_markup=voice_cancellation_button,
                    parse_mode='HTML')
    await state.set_state(VoiceRecordingStates.WAITING_FOR_VOICE)


@router.message(F.voice)
async def handle_voice_message(msg: types.Message, state: FSMContext):
    """Обработчик голосовых сообщений в боте."""
    await msg.chat.delete_message(message_id=msg.message_id - 1)
    
    processor = VoiceProcessor(msg, state)
    await processor.process_voice()


# Обработка для подтверждения
@router.callback_query(lambda c: c.data == 'add_events')
async def process_add_events(callback_query: types.CallbackQuery, state: FSMContext):
    
    await callback_query.message.delete()

    # Узнаём время alerts для th_id
    tg_id = callback_query.from_user.id
    alerts = session.query(UserAlerts).filter(UserAlerts.tg_id == tg_id).first()
    alerts_value = alerts.alerts

    # Добавляет в базу данных событие
    user_data = await state.get_data()
    events_data = user_data.get('events', [])

    # Если это список словарей
    for event in events_data:
        if isinstance(event, dict):
            new_event = Event(
                tg_id=callback_query.from_user.id,
                date=event.get("date"),
                title=event.get("title"),
                description=event.get("description"),
                start_time=event.get("start_time"),
                end_time=event.get("end_time"),
                alerts=event.get("alerts", alerts_value)
            )
            session.add(new_event)
        else:
            print(f"Неверный формат данных для события: {event}")
        
    session.commit()
    session.close()


    await callback_query.message.answer(event_added_message,
                                        reply_markup=platform_button,
                                        parse_mode='HTML')
    await state.clear()


# Обработчик отмены
@router.callback_query(lambda c: c.data == 'cancel_events')
async def process_cancel_events(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.delete()
    
    await callback_query.message.answer(cancel_event_message,
                                        reply_markup=voice_cancellation_button,
                                        parse_mode='HTML')


# Обработчик кнопки "❌ Отменить запись"
@router.message(lambda message: message.text == "❌ Отменить запись")
async def cancel_recording(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == VoiceRecordingStates.WAITING_FOR_VOICE:
        await message.chat.delete_message(message_id=message.message_id - 1)
        await state.clear()
        await message.answer("Вы отменили запись и вернулись в главное меню ☺️", reply_markup=platform_button)