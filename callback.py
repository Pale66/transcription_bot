from aiogram import Bot, F, Router
from aiogram.types import (
    CallbackQuery,
    InaccessibleMessage,
    ReplyParameters,
)

from buttons import delete_button, media_file_buttons, timestamps_check_buttons
from json_db import MessageInfo, get_db
from llm import send_req
from processing import chankify_message, get_transcript_lines

rt = Router()


@rt.callback_query(F.data.startswith("media_"))
async def media_actions(callback: CallbackQuery, bot: Bot):
    db = get_db()
    messages_info = db["messages_info"]
    if not callback.data:
        return
    action, message_unique_id = callback.data.split(sep=":")
    message_info = messages_info.get(message_unique_id)
    action = action.split("_")[1]
    if isinstance(callback.message, InaccessibleMessage) or not callback.message:
        return
    if not message_info or action == "cancel":
        messages_info.pop(message_unique_id, None)
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.edit_text(
            text="File is unaccesible or removed\nSend a new file"
        )
    else:
        if action == "transcription":
            await callback.message.edit_reply_markup(
                reply_markup=timestamps_check_buttons(message_unique_id)
            )
        elif action == "summarize":
            await summarize_action(message_info, bot)


@rt.callback_query(F.data.startswith("timestamps_"))
async def timestamps_actions(callback: CallbackQuery, bot: Bot):
    db = get_db()
    messages_info = db["messages_info"]
    if not callback.data:
        return
    action, message_unique_id = callback.data.split(sep=":")
    message_info = messages_info.get(message_unique_id)
    action = action.split("_")[1] == "True"
    if isinstance(callback.message, InaccessibleMessage) or not callback.message:
        return
    if not message_info or action == "cancel":
        await callback.message.edit_reply_markup(
            reply_markup=media_file_buttons(message_unique_id)
        )
    else:
        await callback.message.edit_reply_markup(
            reply_markup=media_file_buttons(message_unique_id)
        )
        reply_lines = await get_transcript_lines(message_info, bot, action)
        await send_safe_chunks(message_info, bot, reply_lines)


@rt.callback_query(F.data.startswith("delete_"))
async def delete_action(callback: CallbackQuery, bot: Bot):
    if not callback.data:
        return
    data = callback.data.split("_")[1].split(",")
    chat_id = data.pop(0)
    message_ids = data
    for id in message_ids:
        await bot.delete_message(chat_id=chat_id, message_id=int(id))


async def transcription_action(message_info: MessageInfo, bot: Bot, check: bool):
    reply_lines = await get_transcript_lines(message_info, bot, check)
    await send_safe_chunks(message_info, bot, reply_lines)


async def summarize_action(message_info: MessageInfo, bot: Bot):
    transcript_lines = await get_transcript_lines(message_info, bot, False)
    text = "".join(transcript_lines)
    response = send_req(text)
    reply_lines = response.splitlines(keepends=True)
    await send_safe_chunks(message_info, bot, reply_lines)


# TODO: это надо поделить и убрать в модуль
async def send_safe_chunks(
    message_info: MessageInfo, bot: Bot, reply_lines: list[str]
) -> None:
    reply_chunks = chankify_message(reply_lines)
    reply_messages = []
    for reply in reply_chunks:
        reply_messages.append(
            await bot.send_message(
                chat_id=message_info["chat_id"],
                text=reply,
                reply_parameters=ReplyParameters(message_id=message_info["message_id"]),
                disable_notification=True,
            )
        )
    reply_ids = []
    for reply_message in reply_messages:
        reply_ids.append(str(reply_message.message_id))
    await reply_messages[-1].edit_reply_markup(
        reply_markup=delete_button(reply_messages[-1].chat.id, reply_ids)
    )
