from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

router = Router()

# Обработчик команды /start с реферальным кодом
@router.message(Command("start"))
async def start_handler(message: Message, state: FSMContext):
    welcome_message = "Добро пожаловать! ☺️"
    await message.answer(welcome_message)
