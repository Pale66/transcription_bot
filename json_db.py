from typing import TypedDict, NotRequired
import json
from pathlib import Path
from datetime import datetime, UTC, timedelta


class MessageInfo(TypedDict):
    source: str  # NOTE :web or telegram
    source_ref: str
    file_unique_id: str | None
    message_id: int
    chat_id: int
    creation_datetime: str


class FileCache(TypedDict):
    file_name: NotRequired[str]
    transcript_json: list


class JsonDB(TypedDict):
    messages_info: dict[str, MessageInfo]
    file_caches: dict[str, FileCache]


_db: JsonDB | None = None
_workdir: Path | None = None


def create_db(workdir) -> JsonDB:
    assert workdir is not None
    db: JsonDB = {"messages_info": {}, "file_caches": {}}
    save_db()
    return db


def save_db():
    assert _workdir is not None
    db_path = _workdir / "db.json"
    with open(db_path, "w", encoding="UTF-8") as json_file:
        json.dump(_db, json_file, ensure_ascii=False)


def prune_db(db: JsonDB) -> bool:
    expire_days = 7
    cutoff_date = datetime.now(UTC) - timedelta(days=expire_days)
    caches_in_use = set()
    is_updated = False
    for message_unique_id in list(db["messages_info"]):
        message_datetime = datetime.fromisoformat(
            db["messages_info"][message_unique_id]["creation_datetime"]
        )
        if cutoff_date > message_datetime:
            del db["messages_info"][message_unique_id]
            is_updated = True
        else:
            caches_in_use.add(db["messages_info"][message_unique_id]["file_unique_id"])
    for file_unique_id in list(db["file_caches"]):
        if file_unique_id not in caches_in_use:
            is_updated = True
            del db["file_caches"][file_unique_id]
    return is_updated


def load_db(workdir: Path) -> JsonDB:
    assert workdir is not None
    db_path = workdir / "db.json"
    if db_path.is_file():
        with open(db_path, "r", encoding="UTF-8") as json_file:
            db = json.load(json_file)
        print("DB succesfuly loaded from file")
        is_updated = prune_db(db)
        if is_updated:
            print("DB is pruned")
            save_db()
    else:
        db = create_db(workdir)
        print("New DB succesfuly created")
    return db


def init_db(workdir: Path):
    global _db, _workdir
    _workdir = workdir
    _db = load_db(workdir)


def get_db() -> JsonDB:
    assert _db is not None
    return _db
