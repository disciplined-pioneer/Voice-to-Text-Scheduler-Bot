from aiogram.types import Message
from aiogram.filters import Command
from aiogram import F, Router
from aiogram.fsm.context import FSMContext

from db.psql.models.crud import UserChecker
from bot.templates.user.menu import platform_button
from bot.templates.user.instruction_temp import bot_commands_info

router = Router()

@router.message(Command("instruction_router"))
@router.message(F.text == "📕 Инструкция")
async def voice_recording(msg: Message, state: FSMContext):

    tg_id = msg.from_user.id
    checker = UserChecker(tg_id)
    if not checker.user_exists():
        await msg.reply("❌ В доступе отказано, вы не предоставили ключи для подключения к Notion!")
        return

    await msg.reply(bot_commands_info,
                     reply_markup=platform_button,
                     parse_mode='HTML')