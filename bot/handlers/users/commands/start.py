from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from db.psql.models.crud import UserChecker

router = Router()

# Команда start
@router.message(Command("start"))
async def new_user_start(msg: Message, state: FSMContext):
    
    tg_id = msg.from_user.id
    checker = UserChecker(tg_id)
    
    if checker.user_exists():
        welcome_message = "Добро пожаловать, МОЙ ЛЮБИМЫЙ ПОЛЬЗОВАТЕЛЬ! ☺️"
    else:
        welcome_message = "Добро пожаловать, НОВЫЙ ПОЛЬЗОВАТЕЛЬ! ☺️"
    
    # Отправка приветственного сообщения
    await msg.answer(welcome_message)
    checker.close()