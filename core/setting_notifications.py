from datetime import datetime, timedelta
from db.psql.models.models import Event
from apscheduler.schedulers.asyncio import AsyncIOScheduler

class NotificationScheduler:
    
    def __init__(self, bot, session_factory):
        self.bot = bot
        self.session_factory = session_factory
        self.scheduler = AsyncIOScheduler()
        self.scheduler.add_job(self.check_notifications, 'interval', minutes=1)

    async def send_notification(self, user_id, message):
        """Отправка уведомления через Telegram"""
        await self.bot.send_message(user_id, message, parse_mode='HTML')

    async def check_notifications(self):
        """Проверка времени для отправки уведомлений с учётом `alerts`"""
        session = self.session_factory()
        events = session.query(Event).all()
        current_time = datetime.now().strftime('%H:%M')
        current_date = datetime.now().date()

        for event in events:
            event_time = datetime.combine(event.date, event.start_time)
            alert_time = event_time - timedelta(minutes=event.alerts)

            if event.date == current_date and (alert_time.strftime('%H:%M') == current_time or event_time.strftime('%H:%M') == current_time):
                message = f"<b><u>⏰ Напоминание о событии:</u></b>\n\n<b>{event.title}</b>\n - Дата: {event.date}\n - Время: {event.start_time.strftime('%H:%M')}\n - Описание: {event.description}"
            
                await self.send_notification(event.tg_id, message)

    def start(self):
        """Запуск планировщика уведомлений"""
        self.scheduler.start()

