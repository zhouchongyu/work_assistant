from __future__ import annotations

import hashlib
import os
import uuid
from dataclasses import dataclass
from pathlib import Path

import anyio
from fastapi import UploadFile


@dataclass(frozen=True)
class StoredFile:
    file_id: str
    path: str
    md5: str
    size: int
    content_type: str | None
    filename: str | None


def get_storage_dir() -> Path:
    raw = os.environ.get("WA_FILE_STORAGE_DIR") or ".wa_storage"
    return Path(raw)


async def save_upload_file(file: UploadFile, *, storage_dir: Path | None = None) -> StoredFile:
    storage_dir = storage_dir or get_storage_dir()
    storage_dir.mkdir(parents=True, exist_ok=True)

    file_id = uuid.uuid4().hex
    suffix = Path(file.filename or "").suffix
    dest = storage_dir / f"{file_id}{suffix}"

    md5 = hashlib.md5()
    size = 0

    async with await anyio.open_file(dest, "wb") as out:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            md5.update(chunk)
            await out.write(chunk)

    await file.close()

    return StoredFile(
        file_id=file_id,
        path=str(dest),
        md5=md5.hexdigest(),
        size=size,
        content_type=file.content_type,
        filename=file.filename,
    )


async def remove_file(path: str) -> None:
    p = Path(path)
    if not p.exists():
        return
    await anyio.to_thread.run_sync(p.unlink)

