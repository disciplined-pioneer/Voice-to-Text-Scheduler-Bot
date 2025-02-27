from aiogram import F
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.templates.user.menu import schedule_keyboard, platform_button

router = Router()

@router.message(F.text == '📜 Посмотреть записи')
async def voice_recording(msg: Message, state: FSMContext):

    await msg.answer('Выберите период:', reply_markup=schedule_keyboard)


@router.message(F.text == '◀️ Назад')
async def voice_recording(msg: Message, state: FSMContext):

    await msg.answer('Вы вернулись в главное меню 😊', reply_markup=platform_button)