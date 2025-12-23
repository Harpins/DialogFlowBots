import asyncio
from logger import get_logger
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from dialogflowapi import detect_intent_text
from settings import (
    TG_BOT_TOKEN,
    PROJECT_ID,
    LANGUAGE_CODE,
)
from error_bot import send_error_bot_note

logger = get_logger(__name__)


async def cmd_start(message: types.Message):
    await message.answer("Привет! Просто напиши мне что-нибудь!")


async def fetch_df_message(
    message: types.Message, language_code=LANGUAGE_CODE, project_id=PROJECT_ID
):
    chat_id = message.chat.id
    session_id = f"tg_{chat_id}"
    user_text = message.text
    tg_user = message.from_user.id

    try:
        logger.info(f"Пользователь {tg_user} (чат {chat_id}): {user_text}")

        df_response = detect_intent_text(
            project_id=project_id,
            session_id=session_id,
            text=user_text,
            language_code=language_code,
        )

        answer_text = df_response.get("answer_text", "")
        if not answer_text:
            answer_text = "Не могу ответить"
            warning_msg = f"DF не вернул ответ на сообщение '{user_text}' пользователя '{tg_user}'"
            logger.warning(warning_msg)
            await send_error_bot_note(warning_msg)

        await message.answer(answer_text)

    except Exception as e:
        err_msg = (
            f"Ошибка при обработке сообщения от {tg_user}" f"(чат {session_id}): {e}"
        )
        logger.error(err_msg, exc_info=True)
        await send_error_bot_note(err_msg)
        await message.answer("Произошла ошибка при обращении к ИИ")


async def main():

    bot = Bot(token=TG_BOT_TOKEN)
    dp = Dispatcher()

    dp.message.register(cmd_start, Command("start"))
    dp.message.register(fetch_df_message, F.text)

    logger.info("Бот запущен")
    await send_error_bot_note(f"tg-бот запущен")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.critical("Критическая ошибка при tg-polling:", exc_info=True)
        await send_error_bot_note(f"Критическая ошибка при polling tg-бота: {e}")
    finally:
        await bot.session.close()
        stop_message = "tg-бот остановлен"
        logger.info(stop_message)
        await send_error_bot_note(stop_message)


if __name__ == "__main__":
    asyncio.run(main())
