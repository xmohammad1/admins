from aiogram import Router, F
from aiogram.filters.command import CommandStart
from aiogram.types import Message
from utils.lang import MessageTexts

router = Router()


@router.message(F.text, CommandStart())
async def start(message: Message):
    return await message.answer(
        text=MessageTexts.base,
    )
