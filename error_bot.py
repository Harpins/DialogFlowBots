import asyncio
import requests
from logger import get_logger
from aiogram import Bot
from settings import ERROR_BOT_TOKEN, ERROR_CHAT_ID 

logger = get_logger(__name__)
error_bot = Bot(token=ERROR_BOT_TOKEN)

async def send_error_bot_note(message: str):
    try:
        await error_bot.send_message(
            chat_id=ERROR_CHAT_ID,
            text=f"🚨 ОШИБКА В TG БОТЕ 🚨\n\n{message}",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.critical(f"Не удалось отправить уведомление об ошибке: {e}")

def send_error_bot_note_sync(message: str):
    try:
        url = f"https://api.telegram.org/bot{ERROR_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": ERROR_CHAT_ID,
            "text": f"🚨 ОШИБКА В VK БОТЕ 🚨\n\n{message}",
            "parse_mode": "HTML",
        }
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
    except Exception as e:
        logger.critical(f"Ошибка синхронной отправки сообщения боту: {e}")