from pathlib import Path
from uuid import uuid4
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.file_upload import FileUpload

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}


async def save_upload(file: UploadFile, owner_id: int, db: Session) -> str:
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(415, "Only JPEG, PNG, WEBP and GIF images are allowed")

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    content = await file.read()
    if len(content) > max_bytes:
        raise HTTPException(413, f"File exceeds {settings.MAX_UPLOAD_SIZE_MB} MB limit")

    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(file.filename or "").suffix.lower() or ".bin"
    stored_name = f"{uuid4().hex}{suffix}"
    path = upload_dir / stored_name
    path.write_bytes(content)

    db.add(FileUpload(
        owner_id=owner_id,
        original_name=file.filename or "upload",
        stored_name=stored_name,
        mime_type=file.content_type,
        size_bytes=len(content),
        path=str(path),
    ))
    db.flush()
    return f"/uploads/{stored_name}"
