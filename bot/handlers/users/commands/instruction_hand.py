from aiogram.types import Message
from aiogram.filters import Command
from aiogram import F, Router
from aiogram.fsm.context import FSMContext

from bot.templates.user.menu import platform_button
from bot.templates.user.instruction_temp import bot_commands_info

router = Router()

@router.message(Command("instruction_router"))
@router.message(F.text == "📕 Инструкция")
async def voice_recording(msg: Message, state: FSMContext):

    await msg.reply(bot_commands_info,
                     reply_markup=platform_button,
                     parse_mode='HTML')