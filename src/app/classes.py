from enum import Enum
from aiogram.filters.callback_data import CallbackData


class MediaAction(str, Enum):
    TRANSCRIBE = "transcribe"
    SUMMARIZE = "summarize"
    CANCEL = "cancel"


class MediaCallback(CallbackData, prefix="media"):
    action: MediaAction
    chat_id: str
    message_id: str
    timestamps: bool | None = None
