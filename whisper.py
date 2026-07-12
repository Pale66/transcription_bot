from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
import asyncio
from httpx import AsyncClient

from aiogram import Bot

from json_db import FileInfo, get_db, save_db
import ytdlp
from config import whisper_url


async def wav_transcription(
    wav_path: Path, http_client: AsyncClient
) -> list[dict[str, str]]:
    start = datetime.now()
    with wav_path.open("rb") as wav_file:
        files = {"file": wav_file, "response_format": "verbose_json"}
        response = await http_client.post(whisper_url, files=files)
    response.raise_for_status()
    response_json = response.json()
    print("Audio processed in", datetime.now() - start)
    return response_json["segments"]


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
            timestamp_unform = line["start"]
            minutes = int(timestamp_unform // 60)
            seconds = int(timestamp_unform % 60)
            timestamp_form = f"{minutes:02}:{seconds:02}"
            str_line = f"{timestamp_form} {line['text'].strip()}\n"
        else:
            str_line = f"{line['text'].strip()}\n"
        lines_list.append(str_line)
    return lines_list


async def media_to_transcript_json(
    message_info: FileInfo,
    bot: Bot,
    http_client: AsyncClient,
    gpu_semaphore: asyncio.Semaphore,
) -> list:
    source_ref = message_info["source_ref"]
    with TemporaryDirectory(prefix="transcript_") as tempdir:
        tempdir_path = Path(tempdir)
        media_file_path = tempdir_path / "source_file"
        await download_file(message_info["source"], source_ref, media_file_path, bot)
        async with gpu_semaphore:
            wav_path = media_file_path
            transcript_json = await wav_transcription(wav_path, http_client)
    return transcript_json


async def download_file(source, source_ref, media_file_path, bot) -> None:
    if source == "telegram":
        file = await bot.get_file(source_ref)
        await bot.download(file, destination=media_file_path)
    elif source == "web":
        await asyncio.to_thread(ytdlp.download_audio, source_ref, media_file_path)
    else:
        raise ValueError("Wrong source type")
    if not media_file_path.exists():
        raise RuntimeError("No file was downloaded")


async def get_file_unique_id(message_info: FileInfo, bot: Bot) -> str:
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
    file_info: FileInfo,
    bot: Bot,
    timestamps_check: bool,
    http_client: AsyncClient,
    gpu_semaphore: asyncio.Semaphore,
) -> list[str]:
    db = get_db()
    transcript_caches = db["transcript_caches"]
    if not file_info["file_unique_id"]:
        file_info["file_unique_id"] = await get_file_unique_id(file_info, bot)
    file_unique_id = file_info["file_unique_id"]
    if (
        transcript_caches.get(file_unique_id)
        and transcript_caches[file_unique_id]["transcript_json"]
    ):
        file_cache = transcript_caches[file_unique_id]
        transcript_json = file_cache.get("transcript_json")
    else:
        transcript_json = await media_to_transcript_json(
            file_info, bot, http_client, gpu_semaphore
        )
        transcript_caches[file_unique_id] = {"transcript_json": transcript_json}
        save_db()
    reply_lines = json_to_strings(transcript_json, timestamps_check)
    return reply_lines
