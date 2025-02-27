from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import random
import time  # Для контроля времени выполнения программы

# Список случайных событий (вместо базы данных)
events = [
    {"tg_id": 12345, "date": "27.02.2025", "start_time": "21:26", "title": "Встреча с клиентом"},
    {"tg_id": 67890, "date": "27.02.2025", "start_time": "21:27", "title": "Завтрак с коллегами"},
    {"tg_id": 11223, "date": "27.02.2025", "start_time": "21:28", "title": "Рабочий звонок"},
]

# Функция для отправки уведомлений (можно заменить на реальное отправление)
def send_notification(user_id, message):
    """Функция для отправки уведомления (например, выводим на экран)"""
    print(f"Уведомление для пользователя {user_id}: {message}")

# Функция для проверки, нужно ли отправить уведомление
def check_notifications():
    """Проверка времени для отправки уведомлений"""
    current_time = datetime.now().strftime('%H:%M')  # Получаем текущее время в формате ЧЧ:ММ
    print("Текущее время:", current_time)
    current_date = datetime.now().strftime('%d.%m.%Y')  # Получаем текущую дату в формате ДД.ММ.ГГГГ

    # Пробегаем по списку событий и проверяем, совпадает ли время с текущим
    for event in events:
        if event["date"] == current_date and event["start_time"] == current_time:
            message = f"⏰ Напоминание о событии:\n\n<b>{event['title']}</b>\nДата: {event['date']}\nВремя: {event['start_time']}"
            send_notification(event["tg_id"], message)

# Запуск планировщика
scheduler = BackgroundScheduler()
scheduler.add_job(check_notifications, 'interval', minutes=1)

# Запуск планировщика
scheduler.start()

# Чтобы программа продолжала работать и могла завершиться корректно при необходимости
try:
    while True:
        time.sleep(1)  # Ожидание между проверками времени
except (KeyboardInterrupt, SystemExit):
    # Останавливаем планировщик при выходе
    scheduler.shutdown()
    print("Планировщик остановлен.")
