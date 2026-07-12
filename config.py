import json
from dataclasses import dataclass
from dotenv import load_dotenv
from os import getenv


@dataclass
class JsonConfig:
    completion_url: str
    whisper_url: str
    proxy: str
    bot_token: str


load_dotenv()
bot_token = str(getenv("BOT_TOKEN"))


with open("config.json", "r") as f:
    config = JsonConfig(str(getenv("BOT_TOKEN")), **(json.load(f)))
