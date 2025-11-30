
import asyncio
import environs
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

logging.basicConfig(level=logging.INFO)

env = environs.Env()
env.read_env()
TG_BOT_TOKEN = env.str("TG_BOT_TOKEN")

bot = Bot(token=TG_BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я эхобот. Просто напиши мне что-нибудь!")

@dp.message(F.text)
async def echo_message(message: types.Message):
    await message.answer(f"Вы сказали: {message.text}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())




