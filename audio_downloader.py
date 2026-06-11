from sys import argv
from config import PROXY, BASE_DIR
from yt_dlp import YoutubeDL
from pathlib import Path


default_ydl_opts = {"proxy": PROXY}


def is_valid_video(url: str) -> bool:
    ydl_opts = default_ydl_opts | {
        "quiet": True,
        "skip_download": True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=False)
        return True
    except Exception:
        return False


def yt_dlp_download_audio(url: str, output_dir: Path) -> None:
    output_path = output_dir / "source"
    ydl_opts = default_ydl_opts | {
        "outtmpl": str(output_path),
        "format": "bestaudio/best",
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def get_unique_id(url: str) -> str:
    ydl_opts = default_ydl_opts | {}
    with YoutubeDL(ydl_opts) as ydl:
        unique_id = ydl.extract_info(url, download=False)["id"]
    return unique_id


if __name__ == "__main__":
    url = argv[1]
    output_dir = BASE_DIR
    if is_valid_video(url):
        yt_dlp_download_audio(url, output_dir)
    else:
        print("Wrong url")
