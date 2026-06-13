from aiogram import Bot, F, Router
from aiogram.types import (
    CallbackQuery,
    InaccessibleMessage,
    ReplyParameters,
)

from buttons import delete_button, media_file_buttons, timestamps_check_buttons
from json_db import MessageInfo, get_db
from llm import request_summary
from whisper import chankify_message, get_transcript_lines

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


async def summarize_action(message_info: MessageInfo, bot: Bot):
    transcript_lines = await get_transcript_lines(message_info, bot, False)
    text = "".join(transcript_lines)
    response = request_summary(text)
    reply_lines = response.splitlines(keepends=True)
    await send_safe_chunks(message_info, bot, reply_lines)


# TODO: это надо поделить и убрать в модуль
async def send_safe_chunks(
    message_info: MessageInfo, bot: Bot, reply_lines: list[str]
) -> None:
    reply_chunks = chankify_message(reply_lines)
    last_message = ""
    reply_ids = []
    for reply in reply_chunks:
        last_message = await bot.send_message(
            chat_id=message_info["chat_id"],
            text=reply,
            reply_parameters=ReplyParameters(message_id=message_info["message_id"]),
            disable_notification=True,
        )
        reply_ids.append(last_message.message_id)
    if last_message:
        await last_message.edit_reply_markup(
            reply_markup=delete_button(str(message_info["chat_id"]), reply_ids)
        )
    else:
        raise RuntimeError("Не было отправлено ни одно сообщение")
