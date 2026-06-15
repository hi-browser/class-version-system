from pathlib import Path
from uuid import uuid4
from fastapi import UploadFile
from app.core.config import settings

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
VIDEO_SUFFIXES = {".mp4", ".avi", ".mov", ".mkv", ".wmv"}

async def save_upload_file(file: UploadFile) -> tuple[str, str]:
    suffix = Path(file.filename).suffix.lower()
    if suffix in IMAGE_SUFFIXES:
        source_type = "image"
    elif suffix in VIDEO_SUFFIXES:
        source_type = "video"
    else:
        raise ValueError("仅支持 jpg/png/bmp/webp 图片或 mp4/avi/mov/mkv/wmv 视频")

    filename = f"{uuid4().hex}{suffix}"
    save_path = Path(settings.UPLOAD_DIR) / filename

    content = await file.read()
    save_path.write_bytes(content)
    return str(save_path).replace("\\", "/"), source_type
