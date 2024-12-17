# social_api.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from uuid import UUID
import logging
from ...db.database import get_db
from ...db.models import Follow, User
from ...db.schemas import FollowCreate
from ...services.social_service import SocialService
from ...core.exceptions import DatabaseError, ItemNotFoundError

social_router = APIRouter()
logger = logging.getLogger(__name__)

@social_router.post("/follow", response_model=Follow, tags=["Social 🤝"])
def follow_user(follow: FollowCreate, db: Session = Depends(get_db)):
    service = SocialService(db)
    try:
        return service.follow_user(follower_id=follow.follower_id, followed_id=follow.followed_id)
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except ItemNotFoundError as e:
        logger.error(f"Item not found: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@social_router.post("/unfollow", response_model=Follow, tags=["Social 🤝"])
def unfollow_user(follow: FollowCreate, db: Session = Depends(get_db)):
    service = SocialService(db)
    try:
        service.unfollow_user(follower_id=follow.follower_id, followed_id=follow.followed_id)
        return {"message": "Unfollowed successfully"}
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except ItemNotFoundError as e:
        logger.error(f"Item not found: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@social_router.get("/followers/{user_id}", response_model=List[User], tags=["Social 🤝"])
def get_followers(user_id: UUID, db: Session = Depends(get_db)):
    service = SocialService(db)
    try:
        return service.get_followers(user_id)
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except ItemNotFoundError as e:
        logger.error(f"Item not found: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@social_router.get("/following/{user_id}", response_model=List[User], tags=["Social 🤝"])
def get_following(user_id: UUID, db: Session = Depends(get_db)):
    service = SocialService(db)
    try:
        return service.get_following(user_id)
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except ItemNotFoundError as e:
        logger.error(f"Item not found: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))