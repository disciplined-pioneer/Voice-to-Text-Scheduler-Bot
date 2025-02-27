
import os
import shutil

import soundfile as sf
from aiogram import types

from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from config import API_KEY_LLM
from integrations.llm_text import ChatBot

from bot.templates.user.menu import platform_button, voice_cancellation_button, voice_confirmation_button
from bot.templates.user.voice import VoiceRecordingStates
from bot.templates.user.registration import audio_processing_message
from integrations.audio_chunk_processor import process_audio_in_chunks


def generate_event_message(events):
    message = "🚨 <b><u>Подтвердите запись ваших данных:</u></b>\n\n"
    
    # Перебираем все события и формируем сообщение
    for idx, event in enumerate(events, 1):
        title = event.get("title", "Без названия")
        date = event.get("date", "Без даты")
        start_time = event.get("start_time", "Без времени")
        end_time = event.get("end_time", "Без времени")
        description = event.get("description", "Без дополнительной информации.")
        
        # Формируем строку для мероприятия
        event_message = f"{idx}️⃣  <b>{title}</b>\n - Дата: {date}\n - Время: {start_time if start_time else 'Без времени'} - {end_time if end_time else 'Без времени'}\n - Описание: {description}\n\n"
        
        # Добавляем к общему сообщению
        message += event_message
    
    return message


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

        # Сохраняем сообщение, которое отправляем
        reply_message = await self.msg.reply(audio_processing_message, reply_markup=ReplyKeyboardRemove())

        # Скачивание файла
        if not await self.download_voice_file():
            await reply_message.delete()  # Удаляем сообщение
            return await self.msg.reply("Ошибка при скачивании файла.", reply_markup=platform_button)

        # Конвертация в WAV
        wav_path = self.convert_ogg_to_wav()
        if not wav_path:
            await reply_message.delete()  # Удаляем сообщение
            return await self.msg.reply("Ошибка при конвертации файла.", reply_markup=platform_button)

        # Обработка аудио и получение текста
        full_text = process_audio_in_chunks(wav_path)

        # Получение ответа от Llama
        dict_response_AI, result = self.get_llama_response(full_text)

        # Если ответ нормальный
        if result:
            await reply_message.delete()  # Удаляем сообщение
            await self.msg.reply(generate_event_message(dict_response_AI),
                                reply_markup=voice_confirmation_button,
                                parse_mode='HTML')
            
            # Сохраняем данные в состоянии
            await self.state.update_data(events=dict_response_AI)
            
        else:
            await reply_message.delete()  # Удаляем сообщение
            await self.msg.reply(dict_response_AI + '\nОтправьте голосовое ещё раз 🗣',
                                reply_markup=voice_cancellation_button)

        # Очистка данных
        self.cleanup_user_data()
        
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