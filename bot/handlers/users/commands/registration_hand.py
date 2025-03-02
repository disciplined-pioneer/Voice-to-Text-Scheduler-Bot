import re
import asyncio
from aiogram import Router, types
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from aiogram.types import ReplyKeyboardRemove

from db.psql.models.crud import UserChecker
from db.psql.models.models import SessionFactory, User, UserAlerts
from bot.templates.user.menu import platform_button, cancellation_button
from bot.templates.user.registration_temp import (RegistrationState, new_user_message,
                                                existing_user_message, link_message, instruction_id)

# Создание сессии
router = Router()
session = SessionFactory()

# Регулярное выражение для проверки API ключа и ID DB
API_KEY_PATTERN = r"^ntn_[a-zA-Z0-9]+$"
DB_ID_PATTERN = r"^https://www.notion.so/([a-f0-9]{32})\?v="  # Примерный формат ID

# Команда /start
@router.message(Command("start"))
async def new_user_start(msg: Message, state: FSMContext):
    tg_id = msg.from_user.id
    checker = UserChecker(tg_id)
    
    if checker.user_exists():
        await msg.answer(existing_user_message,
                         reply_markup=platform_button,
                         parse_mode='HTML')
    else:
        await msg.answer(new_user_message,
                         parse_mode='HTML')
        
        await asyncio.sleep(1.5)
        await msg.bot.send_document(
            chat_id=tg_id,
            document=instruction_id,
            caption=link_message,
            reply_markup=cancellation_button
        )

        await state.set_state(RegistrationState.waiting_for_api_key)  # Устанавливаем состояние ожидания API ключа

    checker.close()


# Обработчик API ключа
@router.message(RegistrationState.waiting_for_api_key)
async def process_api_key(msg: Message, state: FSMContext):

    if msg.text == "❌ Отменить настройку":
        await cancel_recording(msg, state)
        return

    api_key = msg.text.strip()

    # Проверяем формат API ключа
    if not re.match(API_KEY_PATTERN, api_key):
        await msg.answer("⚠️ Неверный формат API ключа. Пожалуйста, отправьте правильный API ключ",
                     reply_markup=cancellation_button)
        return

    # Сохраняем API ключ
    await state.update_data(api_key=api_key)

    # Переход к следующему шагу
    await state.set_state(RegistrationState.waiting_for_db_id)
    await msg.answer("📝 Пожалуйста, отправьте ID вашей базы данных:",
                     reply_markup=cancellation_button)


# Обработчик ID базы данных
@router.message(RegistrationState.waiting_for_db_id)
async def process_db_id(msg: Message, state: FSMContext):

    if msg.text == "❌ Отменить настройку":
        await cancel_recording(msg, state)
        return

    db_url = msg.text.strip()

    # Проверяем, что ссылка на базу данных соответствует ожидаемому формату
    match = re.match(DB_ID_PATTERN, db_url)
    if not match:
        await msg.answer("⚠️ Неверный формат ID базы данных. Пожалуйста, отправьте корректную ссылку",
                     reply_markup=cancellation_button)
        return

    # Извлекаем ID базы данных
    db_id = match.group(1)

    # Сохраняем ID базы данных
    user_data = await state.get_data()
    tg_id = msg.from_user.id
    api_key = user_data.get("api_key")

    # Добавление данных в базу данных
    session.add(User(tg_id=tg_id, api_key=api_key, db_id=db_id))
    session.add(UserAlerts(tg_id=tg_id, alerts=30))
    session.commit()
    session.close()

    await msg.answer(f"✅ Спасибо! Ваши данные сохранены:\nAPI ключ: {api_key}\nID базы данных: {db_id}",
                     reply_markup=platform_button)
    await state.clear()


# Обработчик кнопки "❌ Отменить настройку"
@router.message(lambda message: message.text == "❌ Отменить настройку")
async def cancel_recording(message: types.Message, state: FSMContext):

    await message.answer("❌ Вы отменили настройку. Но вы можете нажать занова, введя команду /start",
                         reply_markup=ReplyKeyboardRemove())
    await state.clear()