import asyncio
import logging
import sys


from llm import start_llama
from json_db import init_db
from handlers import rt as handlers_rt
from callback import rt as callback_rt
from config import BASE_DIR, PROXY, TOKEN


from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.client.session.aiohttp import AiohttpSession


dp = Dispatcher()
dp.include_routers(handlers_rt, callback_rt)
init_db(BASE_DIR)


async def main() -> None:
    session = AiohttpSession(proxy=PROXY)
    start_llama()
    bot = Bot(
        token=TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        session=session,
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped manually")
