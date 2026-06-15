from sys import argv
from config import PROXY, BASE_DIR
from yt_dlp import YoutubeDL
from typing import TYPE_CHECKING
from pathlib import Path


if TYPE_CHECKING:
    from yt_dlp.YoutubeDL import _Params


default_ydl_opts: _Params = {"proxy": PROXY}


def is_valid_video(url: str) -> bool:
    ydl_opts: _Params = default_ydl_opts | {
        "quiet": True,
        "skip_download": "True",
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=False)
        return True
    except Exception:
        return False


def download_audio(url: str, output_path: Path) -> None:
    if is_valid_video(url):
        ydl_opts = default_ydl_opts | {
            "outtmpl": str(output_path),
            "format": "bestaudio/best",
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    else:
        raise ValueError("Url is unsupported")


def get_unique_id(url: str) -> str:
    ydl_opts = default_ydl_opts | {}
    with YoutubeDL(ydl_opts) as ydl:
        unique_id = ydl.extract_info(url, download=False)["id"]
    return unique_id


if __name__ == "__main__":
    url = argv[1]
    output_dir = BASE_DIR
    if is_valid_video(url):
        download_audio(url, output_dir)
    else:
        print("Wrong url")
