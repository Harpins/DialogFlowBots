import asyncio
from logger import get_logger
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from dialogflowapi import detect_intent_text
from settings import TG_BOT_TOKEN, PROJECT_ID, LANGUAGE_CODE

logger = get_logger(__name__)

bot = Bot(token=TG_BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Просто напиши мне что-нибудь!")

@dp.message(F.text)
async def df_message(message: types.Message):
    session_id = str(message.chat.id)
    user_text = message.text
    tg_user = message.from_user.id

    try:
        logger.info(f"Пользователь {tg_user} (чат {session_id}): {user_text}")

        df_response = detect_intent_text(
            project_id=PROJECT_ID,
            session_id=session_id,
            text=user_text,
            language_code=LANGUAGE_CODE
        )

        answer_text = df_response.get("answer_text", "")
        if not answer_text:
            answer_text = "Не могу ответить"
            logger.warning(f"DF не вернул ответ на сообщение '{user_text}' пользователя '{tg_user}'")

        await message.answer(answer_text)

    except Exception as e:
        
        logger.error(
            f"Ошибка при обработке сообщения от {tg_user} "
            f"(чат {session_id}): {e}",
            exc_info=True  
        )
        await message.answer(
            "Произошла ошибка при обращении к ИИ"
        )

async def main():
    
    logger.info("Бот запущен")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        
        logger.critical("Критическая ошибка при polling:", exc_info=True)
    finally:
        await bot.session.close()
        
        logger.info("Бот остановлен")

if __name__ == "__main__":
    asyncio.run(main())




