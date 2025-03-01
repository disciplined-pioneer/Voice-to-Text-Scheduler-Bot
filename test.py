from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import time

from db.psql.models.models import Event, SessionFactory

session = SessionFactory()
events = session.query(Event).all()

# Преобразование в список словарей
event_list = [
    {key: getattr(event, key) for key in event.__dict__.keys() if not key.startswith("_")}
    for event in events
]

# Функция для отправки уведомлений (можно заменить на реальное отправление)
def send_notification(user_id, message):
    """Функция для отправки уведомления (например, выводим на экран)"""
    print(f"Уведомление для пользователя {user_id}: {message}")

# Функция для проверки, нужно ли отправить уведомление
def check_notifications():
    """Проверка времени для отправки уведомлений с учётом `alerts`"""
    current_time = datetime.now().strftime('%H:%M')  # Текущее время в ЧЧ:ММ
    current_date = datetime.now().date()  # Текущая дата (объект datetime.date)

    print("Текущее время:", current_time)

    for event in events:
        event_time = datetime.combine(event.date, event.start_time)  # Объединяем дату и время
        alert_time = event_time - timedelta(minutes=event.alerts)  # Отнимаем `alerts`
        
        if event.date == current_date and alert_time.strftime('%H:%M') == current_time:
            message = f"⏰ Напоминание о событии:\n\n<b>{event.title}</b>\nДата: {event.date}\nВремя: {event.start_time.strftime('%H:%M')}"
            send_notification(event.tg_id, message)


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
