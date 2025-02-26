
import os
import shutil

from aiogram import F
import soundfile as sf
from aiogram import types

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config import API_KEY_LLM
from integrations.llm_text import ChatBot

from bot.templates.user.menu import voice_button, platform_button

from integrations.audio_chunk_processor import process_audio_in_chunks
from bot.templates.user.registration import audio_processing_message
from bot.templates.user.voice import VoiceRecordingStates, voice_instruction_message


router = Router()


# Команда /voice
@router.message(Command("voice_recording"))
@router.message(F.text == '➕ Добавить запись')
async def voice_recording(msg: Message, state: FSMContext):

    await msg.reply(voice_instruction_message, reply_markup=voice_button)
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
        path = f"data/voices/{str(tg_id)}/{file_id}"
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
            await msg.reply(f"Вот ваш текст: {full_text}", reply_markup=platform_button)

            # Получаем ответ от Llama
            PROMPT_FILE = r"integrations\promp.txt"
            path = rf'data\chats\{str(tg_id)}'
            os.makedirs(path, exist_ok=True)
            HISTORY_FILE = rf"{path}\chat_history_{str(tg_id)}.json"

            # Создание и запуск бота
            bot = ChatBot(API_KEY_LLM, HISTORY_FILE, PROMPT_FILE)
            response_AI = bot.run(full_text)
            print(response_AI)
            await msg.reply(str(response_AI), reply_markup=platform_button)

        except Exception as e:
            await msg.reply(f"Ошибка при конвертации файла: {e}", reply_markup=platform_button)

        # Удаляем папку с аудио файлами
        if os.path.exists(f"data/voices/{str(tg_id)}"):
            shutil.rmtree(f"data/voices/{str(tg_id)}")

         # Удаляем папку с чатом
        if os.path.exists(f"data/chats/{str(tg_id)}"):
            shutil.rmtree(f"data/chats/{str(tg_id)}")
        await state.clear()

    else:
        await msg.reply("Это не голосовое сообщение❌\nПовторите попытку!")


# Обработчик кнопки "❌ Отменить запись"
@router.message(lambda message: message.text == "❌ Отменить запись")
async def cancel_recording(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == VoiceRecordingStates.WAITING_FOR_VOICE:
        await state.clear()
        await message.answer("Запись отменена.", reply_markup=platform_button)