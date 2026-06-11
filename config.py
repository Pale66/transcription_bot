from dotenv import load_dotenv
from pathlib import Path
from os import getenv


load_dotenv()
BASE_DIR = Path(__file__).parent
WHISPER_DIR = BASE_DIR / "whisper.cpp"
WHISPER_BIN = WHISPER_DIR / "whisper-cli.exe"
WHISPER_MODELS_DIR = WHISPER_DIR / "models"
WHISPER_MODEL = "ggml-large-v3-turbo.bin"
WHISPER_MODEL_PATH = WHISPER_MODELS_DIR / WHISPER_MODEL
TOKEN = str(getenv("BOT_TOKEN"))
PROXY = "socks5://127.0.0.1:2080"
LLAMA_EXE = BASE_DIR / "llama.cpp" / "llama-server.exe"
LLM_MODEL_PATH = Path(r"D:\Models\gemma-4-E4B-it-heretic-Q4_K_M.gguf")
