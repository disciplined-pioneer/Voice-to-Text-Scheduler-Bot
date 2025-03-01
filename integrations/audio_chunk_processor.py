import os
import math

import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

from pydub import AudioSegment
import speech_recognition as sr
from concurrent.futures import ThreadPoolExecutor, as_completed


# Функция для распознавания речи из фрагмента аудио
def audio_chunk_to_text(chunk, recognizer):

    try:
        # Используем recognize_google для распознавания
        text = recognizer.recognize_google(chunk, language='ru-RU')
        return text  
    except sr.UnknownValueError:
        return "Не удалось распознать речь"
    except sr.RequestError as e:
        return f"Ошибка сервиса распознавания: {e}"


# Функция для обработки одного фрагмента аудио
def process_audio_chunk(chunk, chunk_index, recognizer, file_path):
    chunk_path = rf"{file_path}/temp_chunk_{chunk_index}.wav"
    chunk.export(chunk_path, format="wav")
    with sr.AudioFile(chunk_path) as source:
        audio_data = recognizer.record(source)
        text = audio_chunk_to_text(audio_data, recognizer)
    return chunk_index, text  # Возвращаем индекс фрагмента и текст


# Функция для разбиения аудио на фрагменты и последовательной обработки с многопоточностью
def process_audio_in_chunks(audio_path, chunk_length=60000):
    
    recognizer = sr.Recognizer()
    wav_path = audio_path

    # Загрузка аудио файла и разбиение на фрагменты
    audio = AudioSegment.from_wav(wav_path)
    audio_length_ms = len(audio)
    num_chunks = math.ceil(audio_length_ms / chunk_length)

    # многопоточная обработка аудиофрагментов
    text_chunks = [None] * num_chunks  # Создаем массив для хранения текста по индексам
    with ThreadPoolExecutor() as executor:
        futures = []
        for i in range(num_chunks):
            start_time = i * chunk_length
            end_time = min((i + 1) * chunk_length, audio_length_ms)
            audio_chunk = audio[start_time:end_time]

            file_path = os.path.dirname(audio_path)
            futures.append(executor.submit(process_audio_chunk, audio_chunk, i, recognizer, file_path))

        for future in as_completed(futures):
            index, chunk_text = future.result()  # Теперь возвращаем индекс и текст
            text_chunks[index] = chunk_text  # Сохраняем текст в правильное место массива

    full_text = " ".join(text_chunks)  # Объединяем текст в правильном порядке
    return full_text
