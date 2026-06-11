from datetime import UTC, datetime

from aiogram import F, Router
from aiogram.enums import ContentType
from aiogram.filters import Command, CommandObject
from aiogram.types import (
    Message,
)

from buttons import media_file_buttons
from json_db import get_db, save_db
from llm import send_req

rt = Router()


@rt.message(Command("summarize"))
async def summarize(message: Message, command: CommandObject):
    text = command.args
    if text:
        response = send_req(text)
        await message.answer(response)


@rt.message(Command("url"))
async def url_dlp(message: Message, command: CommandObject):
    url = command.args
    if url:
        db = get_db()
        messages_info = db["messages_info"]
        try:
            message_unique_id = f"{message.chat.id}-{message.message_id}"
            messages_info[message_unique_id] = {
                "source": "web",
                "source_ref": url,
                "file_unique_id": None,
                "message_id": message.message_id,
                "chat_id": message.chat.id,
                "creation_datetime": datetime.now(UTC).isoformat(),
            }
            await message.answer(
                "Url received\nChoose an action",
                reply_markup=media_file_buttons(message_unique_id),
            )
            save_db()
        except TypeError:
            # But not all the types is supported to be copied so need to handle it
            await message.answer("Some type error")


@rt.message(F.voice | F.audio | F.video | F.video_note)
async def media_file_processing(message: Message) -> None:
    db = get_db()
    messages_info = db["messages_info"]
    try:
        content_type = ContentType(message.content_type).value
        file_instance = getattr(message, message.content_type)
        message_unique_id = f"{message.chat.id}-{message.message_id}"
        messages_info[message_unique_id] = {
            "source": "telegram",
            "source_ref": file_instance.file_id,
            "file_unique_id": None,
            "message_id": message.message_id,
            "chat_id": message.chat.id,
            "creation_datetime": datetime.now(UTC).isoformat(),
        }
        await message.answer(
            f"{content_type.capitalize()} message received\nChoose an action",
            reply_markup=media_file_buttons(message_unique_id),
        )
        save_db()

    except TypeError:
        # But not all the types is supported to be copied so need to handle it
        await message.answer("Some type error")
