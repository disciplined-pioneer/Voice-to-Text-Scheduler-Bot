from aiogram import F
import soundfile as sf
from aiogram import types

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.templates.user.menu import voice_cancellation_button, platform_button
from bot.templates.user.voice import VoiceRecordingStates, voice_instruction_message

from core.voice_processor import VoiceProcessor

router = Router()

# Команда /voice
@router.message(Command("voice_recording"))
@router.message(F.text == '➕ Добавить запись')
async def voice_recording(msg: Message, state: FSMContext):

    await msg.reply(voice_instruction_message, reply_markup=voice_cancellation_button)
    await state.set_state(VoiceRecordingStates.WAITING_FOR_VOICE)


@router.message(F.voice)
async def handle_voice_message(msg: types.Message, state: FSMContext):
    """Обработчик голосовых сообщений в боте."""
    processor = VoiceProcessor(msg, state)
    await processor.process_voice()


# Обработка callback_data в обработчике для "add_events"
@router.callback_query(lambda c: c.data == 'add_events')
async def process_add_events(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.delete()
    await callback_query.message.answer("Мероприятия были успешно добавлены. Все готово!", reply_markup=platform_button)
    await state.clear()  # Очищаем состояние

# Обработка callback_data в обработчике для "cancel_events"
@router.callback_query(lambda c: c.data == 'cancel_events')
async def process_cancel_events(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.delete()
    await callback_query.message.answer("Добавление мероприятий было отменено. ОТправьте горлосове сообщение ещё раз, либо отмените действие", reply_markup=voice_cancellation_button )



# Обработчик кнопки "❌ Отменить запись"
@router.message(lambda message: message.text == "❌ Отменить запись")
async def cancel_recording(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == VoiceRecordingStates.WAITING_FOR_VOICE:
        await state.clear()
        await message.answer("Запись отменена", reply_markup=platform_button)