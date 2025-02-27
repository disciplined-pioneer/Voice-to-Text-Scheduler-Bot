
import os
import shutil

from aiogram import F
import soundfile as sf
from aiogram import types

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.templates.user.menu import voice_button, platform_button
from bot.templates.user.voice import VoiceRecordingStates, voice_instruction_message

from core.voice_llm import VoiceProcessor


router = Router()


# Команда /voice
@router.message(Command("voice_recording"))
@router.message(F.text == '➕ Добавить запись')
async def voice_recording(msg: Message, state: FSMContext):

    await msg.reply(voice_instruction_message, reply_markup=voice_button)
    await state.set_state(VoiceRecordingStates.WAITING_FOR_VOICE)

@router.message(F.voice)
async def handle_voice_message(msg: types.Message, state: FSMContext):
    """Обработчик голосовых сообщений в боте."""
    processor = VoiceProcessor(msg, state)
    await processor.process_voice()

# Обработчик кнопки "❌ Отменить запись"
@router.message(lambda message: message.text == "❌ Отменить запись")
async def cancel_recording(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == VoiceRecordingStates.WAITING_FOR_VOICE:
        await state.clear()
        await message.answer("Запись отменена.", reply_markup=platform_button)