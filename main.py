import asyncio
import logging
import sys
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

TOKEN = os.getenv("BOT_TOKEN")

FREE_NODES = [
    "vless://example-uuid@server-ip:443?encryption=none&security=reality&type=tcp&headerType=none#Free_Server_1"
]

dp = Dispatcher()

@dp.message(Command("start"))
async def command_start_handler(message: types.Message):
    await message.answer(
        "Привет! Я бот для поиска бесплатных серверов для приложения **Happ**.\n\n"
        "Используй команду /free, чтобы получить актуальную конфигурацию."
    )

@dp.message(Command("free"))
async def command_free_handler(message: types.Message):
    if not FREE_NODES:
        await message.answer("Пока нет доступных серверов, попробуй позже.")
        return
    
    node = FREE_NODES[0]
    
    await message.answer(
        f"Вот актуальная бесплатная конфигурация:\n\n`{node}`\n\n"
        "Скопируй её и добавь в приложение Happ.",
        parse_mode=ParseMode.MARKDOWN
    )

async def main():
    if not TOKEN:
        logging.error("Не найден токен бота! Укажи переменную окружения BOT_TOKEN на Render.")
        return
    
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
  
