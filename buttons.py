from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from classes import MediaAction, MediaCallback


def media_file_buttons(chat_id: str, message_id: str):
    summarize_data = MediaCallback(
        action=MediaAction.SUMMARIZE, chat_id=chat_id, message_id=message_id
    )
    transcribe_data = MediaCallback(
        action=MediaAction.TRANSCRIBE, chat_id=chat_id, message_id=message_id
    )
    buttons = [
        [
            InlineKeyboardButton(
                text="Transcribe",
                callback_data=transcribe_data.pack(),
            ),
            InlineKeyboardButton(text="Summarize", callback_data=summarize_data.pack()),
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def delete_group_button():
    buttons = [
        [
            InlineKeyboardButton(
                text="Remove messages",
                callback_data="delete_group",
            ),
        ],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def timestamps_check_buttons(callback_data: MediaCallback):
    buttons = [
        [
            InlineKeyboardButton(
                text="With timestamps",
                callback_data=callback_data.model_copy(
                    update={"timestamps": True}
                ).pack(),
            ),
            InlineKeyboardButton(
                text="Without timestamps",
                callback_data=callback_data.model_copy(
                    update={"timestamps": False}
                ).pack(),
            ),
        ],
        [
            InlineKeyboardButton(
                text="Cancel",
                callback_data=callback_data.model_copy(
                    update={"action": MediaAction.CANCEL}
                ).pack(),
            )
        ],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
