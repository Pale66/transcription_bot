from dotenv import load_dotenv
from pathlib import Path
from os import getenv


load_dotenv()
BASE_DIR = Path(__file__).parent
THIRD_PARTY = BASE_DIR / "Third party"
WHISPER_BIN = THIRD_PARTY / "whisper.cpp" / "whisper-cli.exe"
MODELS_DIR = THIRD_PARTY / "models"
WHISPER_MODEL_NAME = "ggml-large-v3-turbo.bin"
WHISPER_MODEL_PATH = MODELS_DIR / WHISPER_MODEL_NAME
TOKEN = str(getenv("BOT_TOKEN"))
PROXY = "socks5://127.0.0.1:2080"
LLAMA_BIN = THIRD_PARTY / "llama.cpp" / "llama-server.exe"
LLM_MODEL_NAME = "gemma-4-E4B-it.gguf"
LLM_MODEL_PATH = MODELS_DIR / LLM_MODEL_NAME
