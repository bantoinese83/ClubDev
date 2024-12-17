from fastapi import APIRouter, Depends, HTTPException, status, UploadFile
from sqlmodel import Session
import uuid

from ...core.exceptions import DatabaseError, ItemNotFoundError
from ...db.database import get_db
from ...db.schemas import UserRead, UserUpdate
from ...services.user_service import UserService
from ...utils.s3_util import S3Util

user_router = APIRouter()


@user_router.get("/users/{user_id}", response_model=UserRead, tags=["Users 🧑"])
def get_user(*, db: Session = Depends(get_db), user_id: uuid.UUID):
    try:
        s3_util = S3Util()
        user_service = UserService(db, s3_util)
        user = user_service.get_user(user_id)
        if not user:
            raise ItemNotFoundError(f"User with ID {user_id} not found")
        return user
    except ItemNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@user_router.put("/users/{user_id}", response_model=UserRead, tags=["Users 🧑"])
def update_user(*, db: Session = Depends(get_db), user_id: uuid.UUID, user_in: UserUpdate):
    try:
        s3_util = S3Util()
        user_service = UserService(db, s3_util)
        user = user_service.update_user(user_id, user_in)
        if not user:
            raise ItemNotFoundError(f"User with ID {user_id} not found")
        return user
    except ItemNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@user_router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Users 🧑"])
def delete_user(*, db: Session = Depends(get_db), user_id: uuid.UUID):
    try:
        s3_util = S3Util()
        user_service = UserService(db, s3_util)
        user_service.delete_user(user_id)
    except ItemNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@user_router.post("/users/{user_id}/avatar", response_model=UserRead, tags=["Users 🧑"])
def update_user_avatar(*, db: Session = Depends(get_db), user_id: uuid.UUID, avatar: UploadFile):
    try:
        s3_util = S3Util()
        user_service = UserService(db, s3_util)
        user_profile = user_service.update_user_profile(user_id, avatar)
        return user_profile
    except ItemNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))