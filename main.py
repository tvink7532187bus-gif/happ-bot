import asyncio
import logging
import sys
import os
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

TOKEN = os.getenv("BOT_TOKEN")

# Оставляем только рабочие источники
NODES_SOURCES = [
    "https://raw.githubusercontent.com/free-v2ray/v2ray-configs/main/vless.txt",
    "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/Sub1/vless.txt"
]

dp = Dispatcher()

def fetch_nodes():
    for url in NODES_SOURCES:
        try:
            logging.info(f"Пытаемся скачать из: {url}")
            response = requests.get(url, timeout=10)
            logging.info(f"Статус ответа: {response.status_code}")
            
            if response.status_code == 200:
                lines = response.text.splitlines()
                valid_nodes = []
                for line in lines:
                    line = line.strip()
                    if line.startswith("vless://"):
                        valid_nodes.append(line)
                
                if valid_nodes:
                    return valid_nodes[:10]
        except Exception as e:
            logging.error(f"Ошибка при загрузке из {url}: {e}")
            
    return []

@dp.message(Command("start"))
async def command_start_handler(message: types.Message):
    await message.answer(
        "Привет! Я бот для поиска бесплатных серверов для приложения **Happ**.\n\n"
        "Используй команду /free, чтобы получить актуальные конфигурации."
    )

@dp.message(Command("free"))
async def command_free_handler(message: types.Message):
    nodes = fetch_nodes()
    
    if not nodes:
        await message.answer("Пока не удалось получить серверы ни из одного источника. Попробуй позже!")
        return
    
    selected_nodes = nodes[:3]
    
    response_text = "Вот несколько актуальных бесплатных конфигураций:\n\n"
    for i, node in enumerate(selected_nodes, 1):
        response_text += f"**Сервер {i}:**\n`{node}`\n\n"
    
    response_text += "Скопируй любую из них и добавь в приложение Happ."
    
    await message.answer(response_text, parse_mode=ParseMode.MARKDOWN)

async def main():
    if not TOKEN:
        logging.error("Не найден токен бота! Укажи переменную окружения BOT_TOKEN на Render.")
        return
    
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
    
    # Сбрасываем старые зависшие сессии
    await bot.delete_webhook(drop_pending_updates=True)
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
    
