import json
import subprocess
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
import asyncio

from aiogram import Bot

from json_db import MessageInfo, get_db, save_db
from config import WHISPER_BIN, WHISPER_MODEL_PATH
import ytdlp

gpu_semaphore = asyncio.Semaphore(1)


def extract_to_wav(source_path: Path, workdir: Path) -> Path:
    """Принимает путь к аудио/видео и через ffmpeg возвращает путь
    к .wav
    """
    output_audio_path = workdir / "output.wav"
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", source_path, output_audio_path],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            encoding="utf-8",
        )
    except Exception as e:
        print(e)
    return output_audio_path


def wav_transcription(wav_path: Path, workdir: Path) -> list[dict[str, str]]:
    """Принимает путь к .wav, обрабатывает через whipser и возвращает
    список строк транскрипции в видео словарей
    """
    start = datetime.now()
    json_path = workdir / "output"
    try:
        subprocess.run(
            [
                WHISPER_BIN,
                "-m",
                WHISPER_MODEL_PATH,
                "-f",
                wav_path,
                "-of",
                json_path,
                "-l",
                "auto",
                "-t",
                "12",
                "-oj",
            ],
            check=True,
            text=True,
            capture_output=True,
            encoding="utf-8",
        )
        with open(str(json_path) + ".json", "r", encoding="UTF-8") as f:
            transcript_json = json.load(f)["transcription"]
        print("Audio processed in", datetime.now() - start)
        return transcript_json
    except subprocess.CalledProcessError as e:
        print(f"Subprocess error\n{e.output} --- stdout\n{e.stderr} --- stderr")
        raise
    except Exception as e:
        print(e)
        raise


def chankify_message(lines_list: list[str]) -> list[str]:
    """Разбивает транскрипт под размер сообщений телеграма"""
    cur_len = 0
    MAX_LEN = 3593
    temp_chunk = []
    replies_list = []
    for line in lines_list:
        if cur_len + len(line) > MAX_LEN:
            replies_list.append("".join(temp_chunk))
            temp_chunk = []
            cur_len = 0
        cur_len += len(line)
        temp_chunk.append(line)
    if temp_chunk:
        replies_list.append("".join(temp_chunk))
    return replies_list


def json_to_strings(transcript_json: list[dict], with_timestamps: bool) -> list[str]:
    """Разбирает json транскрипции на строки"""
    lines_list = []
    for line in transcript_json:
        if with_timestamps:
            str_line = f"{line['timestamps']['from'].split(',', 1)[0]} {line['text'].strip()}\n"
        else:
            str_line = f"{line['text'].strip()}\n"
        lines_list.append(str_line)
    return lines_list


async def media_to_transcript_json(message_info: MessageInfo, bot: Bot) -> list:
    source_ref = message_info["source_ref"]
    with TemporaryDirectory(prefix="transcript_") as tempdir:
        tempdir_path = Path(tempdir)
        source_file_path = tempdir_path / "source_file"
        await download_file(message_info["source"], source_ref, source_file_path, bot)
        async with gpu_semaphore:
            wav_path = await asyncio.to_thread(
                extract_to_wav, source_file_path, tempdir_path
            )
            transcript_json = await asyncio.to_thread(
                wav_transcription, wav_path, tempdir_path
            )
    return transcript_json


async def download_file(source, source_ref, source_file_path, bot) -> None:
    if source == "telegram":
        file = await bot.get_file(source_ref)
        await bot.download(file, destination=source_file_path)
    elif source == "web":
        await asyncio.to_thread(ytdlp.download_audio, source_ref, source_file_path)
    else:
        raise ValueError("Wrong source type")
    if not source_file_path.exists():
        raise RuntimeError("No file was downloaded")


async def get_file_unique_id(message_info: MessageInfo, bot: Bot) -> str:
    id = None
    source_ref = message_info["source_ref"]
    if message_info["source"] == "telegram":
        file = await bot.get_file(source_ref)
        id = file.file_unique_id
    elif message_info["source"] == "web":
        id = await asyncio.to_thread(ytdlp.get_unique_id, source_ref)
    if id:
        return id
    else:
        raise RuntimeError("No media ID was found")


async def get_transcript_lines(
    message_info: MessageInfo, bot: Bot, timestamps_check: bool
) -> list[str]:
    db = get_db()
    file_caches = db["file_caches"]
    if not message_info["file_unique_id"]:
        message_info["file_unique_id"] = await get_file_unique_id(message_info, bot)
    file_unique_id = message_info["file_unique_id"]
    if (
        file_caches.get(file_unique_id)
        and file_caches[file_unique_id]["transcript_json"]
    ):
        file_cache = file_caches[file_unique_id]
        transcript_json = file_cache.get("transcript_json")
    else:
        transcript_json = await media_to_transcript_json(message_info, bot)
        file_caches[file_unique_id] = {"transcript_json": transcript_json}
        save_db()
    reply_lines = json_to_strings(transcript_json, timestamps_check)
    return reply_lines
