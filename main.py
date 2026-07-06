import asyncio
import logging
import sys


from json_db import init_db
from handlers import rt as handlers_rt
from callback import rt as callback_rt
from config import BASE_DIR, PROXY, TOKEN


from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.client.session.aiohttp import AiohttpSession
from httpx import AsyncClient, Timeout


timeout = Timeout(
        connect=10.0,
        read=300.0,
        write=120.0,
        pool=10.0,
    )
http_client = AsyncClient(timeout=timeout)
dp = Dispatcher(http_client=http_client)
dp.include_routers(handlers_rt, callback_rt)
init_db(BASE_DIR)


async def main() -> None:
    session = AiohttpSession(proxy=PROXY)
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
