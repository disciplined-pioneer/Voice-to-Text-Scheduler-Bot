# Voice-to-Text Scheduler Bot

## Описание проекта
Этот Telegram-бот позволяет пользователям записывать голосовые сообщения, обрабатывать их с помощью модели **meta-llama/Llama-3.3-70B-Instruct-Turbo-Free**, а затем сохранять структурированные заметки в базе данных. Бот также интегрирован с **Notion**, где создаются события в календаре с информацией, полученной из голосовых сообщений. Также реализована система уведомлений и управление записями за разные периоды времени.

## Как это работает
1. **Загрузка голосового сообщения**  
   Голосовое сообщение пользователя загружается в папку временных файлов `data/voice/{user_id}/` в формате `.ogg`.

2. **Конвертация в WAV**  
   Файл конвертируется в формат `.wav` и остается в той же папке.

3. **Разделение аудиофайла**  
   Аудиофайл разделяется на фрагменты по 1 минуте для эффективного распознавания текста в многопоточном режиме.

4. **Преобразование в текст**  
   Фрагменты аудио преобразуются в текст и сохраняются в той же папке.

5. **Обработка текста моделью LLM**  
   Текст передается в LLM-модель с промптом из `integrations/promp.txt`, которая структурирует данные в виде массива словарей:
   ```json
   [
       {
           "title": "Встреча с клиентом",
           "date": "24.12.2025",
           "start_time": "15:00",
           "end_time": "17:00",
           "description": "Возьми с собой документы"
       }
   ]
   ```
6. **Сохранение данных в Notion**  
   Обработанные данные сохраняются как события в календаре Notion с использованием API ключа и ID базы данных, полученных от пользователя.

7. **Удаление временных файлов**  
   После получения всех задач временные файлы автоматически удаляются.

8. **Подтверждение от пользователя**  
   Результат отправляется пользователю, ожидая его подтверждения перед окончательным сохранением.

## Основные функции бота
- Запись и обработка голосовых сообщений.
- Создание и управление задачами в календаре Notion.
- Настройка уведомлений (через кнопки и команды).
- Просмотр записей за различные периоды времени.

## Переменные окружения (.env)
Бот использует переменные окружения для конфигурации:
```
TOKEN = ''  # Токен бота
API_KEY_LLM = ''  # API-ключ модели LLM

ADMIN_LIST = []  # Список администраторов

USER_NAME = ''  # Имя пользователя для БД
PASSWORD_PSQL = ''  # Пароль для PostgreSQL
PORT = ''  # Порт БД
DB_NAME = ''  # Название базы данных
```

## Структура проекта
```
├─── bot
│   ├─── handlers
│   │   └─── users
│   │       └─── commands
│   │           ├─── instruction_hand.py
│   │           ├─── registration_hand.py
│   │           ├─── schedule_handlers.py
│   │           ├─── setting_notifications_hand.py
│   │           └─── voice_recording_hand.py      
│   ├─── templates
│   │   └─── user
│   │       ├─── instruction_temp.py
│   │       ├─── menu.py
│   │       ├─── registration_temp.py
│   │       ├─── setting_notifications_temp.py
│   │       └─── voice_recording_temp.py
│   └─── __init__.py
├─── core
│   ├─── setting_notifications.py
│   └─── voice_processor.py
├─── data
│   ├─── chats
│   └─── voices
├─── db
│   └─── psql
│       └─── models
│           ├─── crud.py
│           └─── models.py
├─── integrations
│   ├─── audio_chunk_processor.py
│   ├─── llm_chatbot.py
│   ├─── notion_event.py
│   └─── promp.txt
├─── .env
├─── .gitignore
├─── README.md
├─── bot.py
├─── config.py
└─── requirements.txt
```

## Установка и запуск
1. **Клонируйте репозиторий**
   ```sh
   https://github.com/disciplined-pioneer/Voice-to-Text-Scheduler-Bot.git
   cd Voice-to-Text-Scheduler-Bot
   ```
2. **Создайте виртуальное окружение и установите зависимости**
   ```sh
   python -m venv venv
   source venv/bin/activate  # Для Linux/Mac
   venv\Scripts\activate  # Для Windows
   pip install -r requirements.txt
   ```
3. **Заполните `.env` файл** (пример значений указан выше).
4. **Запустите бота**
   ```sh
   python bot.py
   ```
5. **Папка 'data' и её содержимое будет создано при обработке аудиио. Она хранит временные файлы для голосовых сообщений и чатов пользователей**
