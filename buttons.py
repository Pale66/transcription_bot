from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


def media_file_buttons(message_unique_id: str):
    buttons = [
        [
            InlineKeyboardButton(
                text="Transcription",
                callback_data=f"media_transcription:{message_unique_id}",
            ),
            InlineKeyboardButton(
                text="Summarize", callback_data=f"media_summarize:{message_unique_id}"
            ),
        ],
        # [InlineKeyboardButton(text="Cancel", callback_data=f"media_cancel:{task_id}")],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def delete_button(chat_id: str, message_ids: list[str]):
    callback_data = f"{chat_id},{','.join(message_ids)}"
    if len(message_ids) > 1:
        buttons = [
            [
                InlineKeyboardButton(
                    text="Remove messages",
                    callback_data=f"delete_{callback_data}",
                ),
            ],
        ]
    else:
        buttons = [
            [
                InlineKeyboardButton(
                    text="Remove message",
                    callback_data=f"delete_{callback_data}",
                ),
            ],
        ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def timestamps_check_buttons(message_unique_id: str):
    buttons = [
        [
            InlineKeyboardButton(
                text="With timestamps",
                callback_data=f"timestamps_True:{message_unique_id}",
            ),
            InlineKeyboardButton(
                text="Without timestamps",
                callback_data=f"timestamps_False:{message_unique_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Cancel", callback_data=f"timestamps_cancel:{message_unique_id}"
            )
        ],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
