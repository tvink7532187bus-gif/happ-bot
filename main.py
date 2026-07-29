import asyncio
import logging
import sys
import os
import threading
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

TOKEN = os.getenv("BOT_TOKEN")

# Актуальные источники конфигураций
NODES_SOURCES = [
    "https://raw.githubusercontent.com/ALIILAPRO/v2ray-configs/main/sub/vless.txt",
    "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/Sub/vless.txt"
]

# 1. Мини-сервер для того, чтобы Render был доволен открытым портом
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")
    def log_message(self, format, *args):
        pass  # Отключаем лишние логи веб-сервера в консоли

def start_web_server():
    port = int(os.getenv("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

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
                
                logging.info(f"Найдено подходящих vless://: {len(valid_nodes)}")
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
    
    # Запускаем веб-сервер в фоновом потоке, чтобы Render не ругался на порты
    threading.Thread(target=start_web_server, daemon=True).start()
    
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
    
    # Сбрасываем старые зависшие сессии
    await bot.delete_webhook(drop_pending_updates=True)
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
    
