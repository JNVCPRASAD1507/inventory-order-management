from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.auth import UserResponse
from app.utils.files import save_upload

router = APIRouter(prefix="/files", tags=["Files"])


@router.post("/profile-image", response_model=UserResponse)
async def upload_profile_image(file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    path = await save_upload(file, user.id, db)
    user.profile_image = path
    db.commit(); db.refresh(user)
    return user
