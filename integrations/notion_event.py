import requests
from datetime import datetime, time

import logging
logging.basicConfig(level=logging.CRITICAL)


def transform_event_data(event):

    """Преобразует данные события в формат, подходящий для функции add_event."""
    
    # Преобразуем дату в формат YYYY-MM-DD
    event_date = datetime.strptime(event['date'], "%d.%m.%Y").date()

    # Если время начала события есть, преобразуем его в формат HH:MM
    if event['start_time']:
        try:
            event_start_time = datetime.strptime(event['start_time'], "%H:%M").time()
        except ValueError:
            event_start_time = time(0, 0)
    else:
        event_start_time = time(0, 0)

    # Преобразуем в строку для Notion в формате ISO 8601 (например, 2025-03-02T19:00)
    start_date_time_str = datetime.combine(event_date, event_start_time).isoformat()

    # Если время окончания есть, преобразуем его в формат ISO 8601
    if event['end_time']:
        try:
            event_end_time = datetime.strptime(event['end_time'], "%H:%M").time()
            end_date_time_str = datetime.combine(event_date, event_end_time).isoformat()
        except ValueError:
            end_date_time_str = None
    else:
        end_date_time_str = None

    # Возвращаем преобразованные данные для передачи в add_eventЦ
    return {
        "name": event['title'],
        "start_date": start_date_time_str,
        "end_date": end_date_time_str
    }


def add_event(name: str, start_date: str = None, end_date: str = None,
              NOTION_API_KEY: str = None, DATABASE_ID: str = None):
    
    """Добавляет событие в Notion"""


    HEADERS = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    if not name:
        print("❌ Ошибка: У события должно быть название!")
        return

    event_data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name": {"title": [{"text": {"content": name}}]}
        }
    }

    # Если есть дата, добавляем её в запрос
    if start_date:
        event_data["properties"]["Date"] = {
            "date": {"start": start_date, "end": end_date if end_date else None}
        }

    response = requests.post("https://api.notion.com/v1/pages", headers=HEADERS, json=event_data)

    if response.status_code != 200:
        return False

    print("✅ Событие успешно добавлено!")
    return True  # Возвращаем True при успешном добавлении события
