import asyncio

from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery, ReplyParameters, Message, reply_parameters
from httpx import AsyncClient

from buttons import delete_group_button, media_file_buttons, timestamps_check_buttons
from json_db import MessageData, get_db, JsonDB, save_db
from llm import request_summary
from whisper import chankify_message, get_transcript_lines
from classes import MediaAction, MediaCallback

rt = Router()


@rt.callback_query(MediaCallback.filter(F.action == MediaAction.TRANSCRIBE))
async def transcribe_action(
    callback: CallbackQuery,
    bot: Bot,
    http_client: AsyncClient,
    gpu_semaphore: asyncio.Semaphore,
    callback_data: MediaCallback,
    db: JsonDB,
):
    message = callback.message
    if not isinstance(message, Message):
        return
    if callback_data.timestamps is None:
        await message.edit_reply_markup(
            reply_markup=timestamps_check_buttons(callback_data)
        )
        return
    chats = db["chats"]
    chat_id = callback_data.chat_id
    message_id = callback_data.message_id
    messages = chats.get(chat_id)
    if not messages:
        return
    message_data = messages.get(message_id)
    if not message_data:
        await bot.delete_message(chat_id, int(message_id))
        return
    file_info = message_data.get("file_info")
    if not file_info:
        return
    await message.edit_reply_markup(
        reply_markup=media_file_buttons(chat_id, message_id)
    )
    processing_message = await send_proccesing_message(message)

    try:
        transcript_lines = await get_transcript_lines(
            file_info,
            bot,
            callback_data.timestamps,
            http_client,
            gpu_semaphore,
        )
        await send_safe_chunks(messages, chat_id, message_id, bot, transcript_lines)
    except Exception as e:
        await message.answer(f"Error: {e}")
        print(f"{type(e).__name__}: error type")
        print(f"{repr(e)}: error repr")
    finally:
        await bot.delete_message(message.chat.id, processing_message.message_id)


@rt.callback_query(MediaCallback.filter(F.action == MediaAction.SUMMARIZE))
async def summarize_actions(
    callback: CallbackQuery,
    bot: Bot,
    http_client: AsyncClient,
    gpu_semaphore: asyncio.Semaphore,
    callback_data: MediaCallback,
    db: JsonDB,
):
    db = get_db()
    chats = db["chats"]
    chat_id = callback_data.chat_id
    message_id = callback_data.message_id
    chats = chats.get(chat_id)
    if not chats:
        return
    message_data = chats.get(message_id)
    message = callback.message
    if not message_data:
        return
    if not isinstance(message, Message):
        return
    file_info = message_data.get("file_info")
    if file_info:
        proccessing_message = await send_proccesing_message(message)
        transcript_lines = await get_transcript_lines(
            file_info, bot, False, http_client, gpu_semaphore
        )
        text = "".join(transcript_lines)
        response = await request_summary(text, http_client, gpu_semaphore)
        reply_lines = response.splitlines(keepends=True)
        await send_safe_chunks(chats, chat_id, message_id, bot, reply_lines)
        await bot.delete_message(chat_id, proccessing_message.message_id)
    else:
        raise RuntimeError("File info should exist")


@rt.callback_query(MediaCallback.filter(F.action == MediaAction.CANCEL))
async def cancel_action(
    callback: CallbackQuery,
    callback_data: MediaCallback,
):
    message = callback.message
    if not isinstance(message, Message):
        return
    else:
        chat_id = callback_data.chat_id
        message_id = callback_data.message_id
        await message.edit_reply_markup(
            reply_markup=media_file_buttons(chat_id, message_id)
        )


@rt.callback_query(F.data == "delete_group")
async def delete_action(callback: CallbackQuery, bot: Bot, db: JsonDB):
    if not callback.data or not callback.message:
        return
    chat_id = str(callback.message.chat.id)
    message_id = str(callback.message.message_id)
    message_info = db["chats"][chat_id][message_id]
    message_ids = message_info.get("message_group")
    if message_ids:
        for id in message_ids:
            await bot.delete_message(chat_id=chat_id, message_id=int(id))
    else:
        raise RuntimeError(
            "Message group should exist for delete button message "
            f"(chat_id={chat_id}, message_id={message_id})."
        )


async def send_proccesing_message(message: Message):
    proccessing_message = await message.answer(
        text="Processing in progress...",
        reply_parameters=ReplyParameters(message_id=message.message_id),
    )
    return proccessing_message


async def send_safe_chunks(
    chat_messages: dict[str, MessageData],
    chat_id: str,
    message_id: str,
    bot: Bot,
    reply_lines: list[str],
) -> None:
    reply_chunks = chankify_message(reply_lines)
    last_message = ""
    reply_ids = []
    for reply in reply_chunks:
        last_message = await bot.send_message(
            chat_id=chat_id,
            text=f"<blockquote expandable>{reply}</blockquote>",
            reply_parameters=ReplyParameters(message_id=int(message_id)),
            disable_notification=True,
            parse_mode="HTML",
        )
        reply_ids.append(str(last_message.message_id))
    if last_message:
        last_message_id = str(last_message.message_id)
        chat_messages[last_message_id] = {"message_group": reply_ids}
        save_db()
        await last_message.edit_reply_markup(reply_markup=delete_group_button())
    else:
        raise RuntimeError("No messages was sent")
