
import os
import shutil

from aiogram import F
import soundfile as sf
from aiogram import types

from aiogram.fsm.context import FSMContext

from config import API_KEY_LLM
from integrations.llm_text import ChatBot

from bot.templates.user.menu import platform_button

from integrations.audio_chunk_processor import process_audio_in_chunks
from bot.templates.user.registration import audio_processing_message
from bot.templates.user.voice import VoiceRecordingStates


class VoiceProcessor:
    
    """Класс для обработки голосовых сообщений."""
    
    def __init__(self, msg: types.Message, state: FSMContext):
        self.msg = msg
        self.state = state
        self.tg_id = msg.from_user.id
        self.file_id = msg.voice.file_id
        self.voice_path = f"data/voices/{self.tg_id}"
        self.chat_path = f"data/chats/{self.tg_id}"

    async def process_voice(self):
        """Основной метод обработки голосового сообщения."""
        if await self.state.get_state() != VoiceRecordingStates.WAITING_FOR_VOICE:
            return

        await self.msg.reply(audio_processing_message)

        # Скачивание файла
        if not await self.download_voice_file():
            return await self.msg.reply("Ошибка при скачивании файла.", reply_markup=platform_button)

        # Конвертация в WAV
        wav_path = self.convert_ogg_to_wav()
        if not wav_path:
            return await self.msg.reply("Ошибка при конвертации файла.", reply_markup=platform_button)

        # Обработка аудио и получение текста
        full_text = process_audio_in_chunks(wav_path)
        await self.msg.reply(f"Вот ваш текст: {full_text}")

        # Получение ответа от Llama
        response_AI = self.get_llama_response(full_text)
        await self.msg.reply(str(response_AI), reply_markup=platform_button)

        # Очистка данных
        self.cleanup_user_data()
        await self.state.clear()

    async def download_voice_file(self) -> bool:
        """Скачивает голосовой файл и сохраняет его."""
        try:
            os.makedirs(self.voice_path, exist_ok=True)
            file = await self.msg.bot.get_file(self.file_id)
            destination = os.path.join(self.voice_path, f"{self.file_id}.ogg")
            await self.msg.bot.download_file(file.file_path, destination)
            return True
        except Exception as e:
            print(f"Ошибка скачивания файла: {e}")
            return False

    def convert_ogg_to_wav(self) -> str:
        """Конвертирует OGG в WAV и возвращает путь к файлу."""
        try:
            ogg_path = os.path.join(self.voice_path, f"{self.file_id}.ogg")
            data, samplerate = sf.read(ogg_path)
            wav_path = ogg_path.replace(".ogg", ".wav")
            sf.write(wav_path, data, samplerate)
            return wav_path
        except Exception as e:
            print(f"Ошибка конвертации: {e}")
            return ""

    def get_llama_response(self, text: str) -> str:
        """Запрашивает ответ у Llama на основе переданного текста."""
        os.makedirs(self.chat_path, exist_ok=True)
        bot = ChatBot(API_KEY_LLM, f"{self.chat_path}/chat_history_{self.tg_id}.json", r"integrations/promp.txt")
        return bot.run(text)

    def cleanup_user_data(self):
        """Удаляет временные данные пользователя."""
        shutil.rmtree(self.voice_path, ignore_errors=True)
        shutil.rmtree(self.chat_path, ignore_errors=True)