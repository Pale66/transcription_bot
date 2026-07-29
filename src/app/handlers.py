import asyncio
from datetime import UTC, datetime

from aiogram import F, Router
from aiogram.enums import ContentType
from aiogram.filters import Command, CommandObject
from aiogram.types import (
    Message,
    ReplyParameters,
    reply_parameters,
)
from httpx import AsyncClient

from buttons import media_file_buttons
from json_db import MessageData, get_db, save_db, FileInfo
from llm import request_summary

rt = Router()


@rt.message(Command("summarize"))
async def summarize(
    message: Message,
    command: CommandObject,
    http_client: AsyncClient,
    gpu_semaphore: asyncio.Semaphore,
):
    text = command.args
    if text:
        response = await request_summary(text, http_client, gpu_semaphore)
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


# TODO: do something
async def manage_media(message: Message, source: str, source_ref, content_type) -> None:
    db = get_db()
    chats = db["chats"]
    message_id = str(message.message_id)
    chat_id = str(message.chat.id)
    file_info: FileInfo = {
        "source": source,
        "source_ref": source_ref,
        "file_unique_id": None,
        "creation_datetime": datetime.now(UTC).isoformat(),
    }
    message_data: MessageData = {"file_info": file_info}
    if not chats.get(chat_id):
        chats[chat_id] = {}
    chats[chat_id].update({message_id: message_data})
    await message.answer(
        f"{content_type} message received\nChoose an action",
        reply_markup=media_file_buttons(chat_id, message_id),
        reply_parameters=ReplyParameters(message_id=int(message_id)),
    )
    save_db()
