
import os
from aiogram import F
import soundfile as sf
from aiogram import types

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from core.audio_chunk_processor import process_audio_in_chunks
from bot.templates.user.registration import audio_processing_message
from bot.templates.user.voice import VoiceRecordingStates, voice_instruction_message


router = Router()


# Команда /voice
@router.message(Command("voice_recording"))
@router.message(F.text == '➕ Добавить запись')
async def voice_recording(msg: Message, state: FSMContext):

    await msg.reply(voice_instruction_message)
    await state.set_state(VoiceRecordingStates.WAITING_FOR_VOICE)



@router.message(F.voice)
async def download_voice(msg: types.Message, state: FSMContext):

    current_state = await state.get_state()
    if current_state == VoiceRecordingStates.WAITING_FOR_VOICE and msg.voice:
        await msg.reply(audio_processing_message)

        tg_id = msg.from_user.id
        voice = msg.voice
        file_id = voice.file_id
        file = await msg.bot.get_file(file_id)

        # Папка для сохранения голосовых файлов
        path = f"db/voices/{str(tg_id)}/{file_id}"
        os.makedirs(path, exist_ok=True)

        # Скачиваем файл
        file_path = file.file_path
        destination = os.path.join(path, f"{file_id}.ogg")

        await msg.bot.download_file(file_path=file_path, destination=destination)

        # Чтение файла с помощью soundfile
        try:
            data, samplerate = sf.read(destination)  # Чтение ogg файла
            wav_destination = os.path.join(path, f"{file_id}.wav")
            sf.write(wav_destination, data, samplerate)  # Запись в wav

            # Перевод аудио в текст
            full_text = process_audio_in_chunks(path + f'/{file_id}.wav')
            await msg.reply(f"Вот твой текст: {full_text}")

        except Exception as e:
            await msg.reply(f"Ошибка при конвертации: {e}")
        await state.clear()
    else:
        await msg.reply("Это не голосовое сообщение.")
