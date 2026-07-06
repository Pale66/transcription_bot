from dotenv import load_dotenv
from pathlib import Path
from os import getenv


load_dotenv()
completion_url = r"http://127.0.0.1:5001/v1/chat/completions"
whisper_url = r"http://127.0.0.1:5067/inference"
base_dir = Path(__file__).parent
token = str(getenv("BOT_TOKEN"))
proxy = "socks5://127.0.0.1:2080"
