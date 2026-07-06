from datetime import UTC, datetime

from aiogram import F, Router
from aiogram.enums import ContentType
from aiogram.filters import Command, CommandObject
from aiogram.types import (
    Message,
)
from httpx import AsyncClient

from buttons import media_file_buttons
from json_db import get_db, save_db
from llm import request_summary

rt = Router()


@rt.message(Command("summarize"))
async def summarize(message: Message, command: CommandObject, http_client: AsyncClient):
    text = command.args
    if text:
        response = await request_summary(text, http_client)
        await message.answer(response)


@rt.message(Command("url"))
async def url_dlp(message: Message, command: CommandObject):
    url = command.args
    if url:
        await manage_media(message, "web", url, "URL")


@rt.message(Command("test"))
async def test_handl(message: Message):
    await message.answer("Test message")


@rt.message(F.voice | F.audio | F.video | F.video_note)
async def media_file_processing(message: Message) -> None:
    content_type = ContentType(message.content_type).value
    file_id = getattr(message, message.content_type).file_id
    await manage_media(message, "telegram", file_id, content_type.capitalize())


async def manage_media(message: Message, source: str, source_ref, content_type) -> None:
    db = get_db()
    messages_info = db["messages_info"]
    message_unique_id = f"{message.chat.id}-{message.message_id}"
    messages_info[message_unique_id] = {
        "source": source,
        "source_ref": source_ref,
        "file_unique_id": None,
        "message_id": message.message_id,
        "chat_id": message.chat.id,
        "creation_datetime": datetime.now(UTC).isoformat(),
    }
    await message.answer(
        f"{content_type} message received\nChoose an action",
        reply_markup=media_file_buttons(message_unique_id),
    )
    save_db()
