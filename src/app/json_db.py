from typing import TypedDict, NotRequired
import json
from pathlib import Path
from datetime import datetime, UTC, timedelta


class FileInfo(TypedDict):
    source: str  # NOTE :web or telegram
    source_ref: str
    file_unique_id: str | None
    creation_datetime: str


class FileCache(TypedDict):
    transcript_json: list


class MessageData(TypedDict):
    file_info: NotRequired[FileInfo]
    message_group: NotRequired[list]


class JsonDB(TypedDict):
    chats: dict[str, dict[str, MessageData]]
    transcript_caches: dict[str, FileCache]


db: JsonDB | None = None
_db_path: Path | None = None


def create_db() -> JsonDB:
    db: JsonDB = {"chats": {}, "transcript_caches": {}}
    return db


def save_db():
    db_path = _db_path
    if not db_path:
        raise RuntimeError("DB wasn't created")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with db_path.open("w", encoding="UTF-8") as json_file:
        json.dump(db, json_file, ensure_ascii=False)


def prune_db(db: JsonDB) -> bool:
    return False  # TODO: Rework needed
    expire_days = 7
    cutoff_date = datetime.now(UTC) - timedelta(days=expire_days)
    caches_in_use = set()
    is_updated = False
    if db["chats"]:
        for chat_id in list(db["chats"]):
            if db["chats"][chat_id]:
                for message_id in list(db["chats"][chat_id]):
                    message_datetime = datetime.fromisoformat(
                        db["chats"][chat_id][message_id]["creation_datetime"]
                    )
                    if cutoff_date > message_datetime:
                        del db["chats"][chat_id][message_id]
                        if not db["chats"][chat_id]:
                            del db["chats"][chat_id]
                        is_updated = True
                    else:
                        caches_in_use.add(
                            db["chats"][chat_id][message_id]["file_unique_id"]
                        )
    for file_unique_id in list(db["transcript_caches"]):
        if file_unique_id not in caches_in_use:
            is_updated = True
            del db["transcript_caches"][file_unique_id]
    return is_updated


def load_db(db_path: Path) -> JsonDB:
    if db_path.is_file():
        with open(db_path, "r", encoding="UTF-8") as json_file:
            db = json.load(json_file)
        print("DB succesfuly loaded from file")
        is_updated = prune_db(db)
        if is_updated:
            print("DB is pruned")
            save_db()
    else:
        db = create_db()
        print("New DB succesfuly created")
    return db


def init_db(db_path: Path):
    global db, _db_path
    _db_path = db_path
    db = load_db(db_path)
    return db


def get_db() -> JsonDB:
    assert db is not None
    return db
