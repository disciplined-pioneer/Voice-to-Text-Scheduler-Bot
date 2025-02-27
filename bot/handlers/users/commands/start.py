import asyncio
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from db.psql.models.crud import UserChecker
from db.psql.models.models import SessionFactory, User
from bot.templates.user.registration import RegistrationState

from bot.templates.user.menu import platform_button
from bot.templates.user.registration import ( new_user_message, existing_user_message,
                                             instruction_id, link_message)


# Создание сессии
session = SessionFactory()

router = Router()

# Команда /start
@router.message(Command("start"))
async def new_user_start(msg: Message, state: FSMContext):
    tg_id = msg.from_user.id
    checker = UserChecker(tg_id)
    
    if checker.user_exists():
        await msg.answer(existing_user_message,
                         reply_markup=platform_button)
    else:
        await msg.answer(new_user_message)
        
        await asyncio.sleep(1.5)
        await msg.bot.send_document(
            chat_id=tg_id,
            document=instruction_id,
            caption=link_message
        )

        await state.set_state(RegistrationState.waiting_for_address)  # Устанавливаем состояние ожидания

    checker.close()


# Обработчик ссылки на календарь
@router.message(RegistrationState.waiting_for_address)
async def process_address(msg: Message, state: FSMContext):

    # Проверяем, содержит ли адрес нужный фрагмент
    address = msg.text.strip()
    if "https://calendar.google.com/calendar/" in address:

        # Добавление в базу данных
        tg_id = msg.from_user.id
        new_user = User(tg_id=tg_id, key_calendar=address)
        session.add(new_user)
        session.commit()
        session.close()

        await msg.answer(f"✅ Спасибо! Ваш календарь сохранён:\n{address}",
                         reply_markup=platform_button)
        await state.clear()
    else:
        await msg.answer("⚠️ Ошибка! Отправьте корректную ссылку Google Calendar с вашим адресом")

