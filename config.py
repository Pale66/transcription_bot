from dataclasses import dataclass
from dotenv import load_dotenv
from os import getenv


@dataclass
class Config:
    completion_url: str
    whisper_url: str
    proxy_url: str | None
    bot_token: str


load_dotenv()
whisper_url = "http://127.0.0.1:5067/"
completion_url = "http://127.0.0.1:5001/"
bot_token = getenv("BOT_TOKEN")
if not bot_token:
    raise RuntimeError("BOT_TOKEN is required")
whisper_url = getenv("WHISPER_URL", whisper_url)
completion_url = getenv("COMPLETION_URL", completion_url)
proxy_url = getenv("PROXY_URL") or None

config = Config(
    bot_token=bot_token,
    completion_url=completion_url,
    whisper_url=whisper_url,
    proxy_url=proxy_url,
)
