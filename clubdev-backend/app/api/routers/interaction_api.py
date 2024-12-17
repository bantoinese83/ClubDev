from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from ...api.deps import validate_user_id
from ...core.exceptions import DatabaseError, ItemNotFoundError
from ...db.database import get_db
from ...db.models import Like, Comment, Flag
from ...db.schemas import LikeRequest, CommentRequest, FlagRequest
from ...services.interaction_service import InteractionService

interaction_router = APIRouter()

@interaction_router.post("/like", response_model=Like, tags=["Interactions 👍👎"])
def like_content(request: LikeRequest, db: Session = Depends(get_db)):
    validate_user_id(request.user_id, db)
    service = InteractionService(db)
    try:
        return service.like_content(request.user_id, request.content_id, request.content_type)
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except ItemNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@interaction_router.delete("/unlike", status_code=status.HTTP_204_NO_CONTENT, tags=["Interactions 👍👎"])
def unlike_content(request: LikeRequest, db: Session = Depends(get_db)):
    validate_user_id(request.user_id, db)
    service = InteractionService(db)
    try:
        service.unlike_content(request.user_id, request.content_id, request.content_type)
        return {"message": "Content unliked successfully"}
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except ItemNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@interaction_router.post("/comment", response_model=Comment, tags=["Interactions ✏️💬🗑️️"])
def comment_on_content(request: CommentRequest, db: Session = Depends(get_db)):
    validate_user_id(request.user_id, db)
    service = InteractionService(db)
    try:
        return service.comment_on_content(request.user_id, request.content_id, request.content_type, request.comment_text)
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except ItemNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@interaction_router.put("/comment/{comment_id}", response_model=Comment, tags=["Interactions ✏️💬🗑️️"])
def update_comment(user_id: UUID, comment_id: UUID, comment_text: str, db: Session = Depends(get_db)):
    service = InteractionService(db)
    try:
        return service.update_comment(user_id, comment_id, comment_text)
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except ItemNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@interaction_router.delete("/comment/{comment_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Interactions ✏️💬🗑️️"])
def delete_comment(user_id: UUID, comment_id: UUID, db: Session = Depends(get_db)):
    service = InteractionService(db)
    try:
        service.delete_comment(user_id, comment_id)
        return {"message": "Comment deleted successfully"}
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except ItemNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@interaction_router.post("/flag", response_model=Flag, tags=["Interactions 🚩"])
def flag_content(request: FlagRequest, db: Session = Depends(get_db)):
    validate_user_id(request.user_id, db)
    service = InteractionService(db)
    try:
        return service.flag_content(request.user_id, request.content_id, request.content_type, request.reason)
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except ItemNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@interaction_router.get("/likes/{content_id}", response_model=List[Like], tags=["Interactions 👍 💬"])
def get_likes_for_content(content_id: UUID, content_type: str, db: Session = Depends(get_db)):
    service = InteractionService(db)
    try:
        return service.get_likes_for_content(content_id, content_type)
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except ItemNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@interaction_router.get("/comments/{content_id}", response_model=List[Comment], tags=["Interactions 👍 💬"])
def get_comments_for_content(content_id: UUID, content_type: str, db: Session = Depends(get_db)):
    service = InteractionService(db)
    try:
        return service.get_comments_for_content(content_id, content_type)
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except ItemNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@interaction_router.get("/flags/{content_id}", response_model=List[Flag], tags=["Interactions 🚩"])
def get_flags_for_content(content_id: UUID, content_type: str, db: Session = Depends(get_db)):
    service = InteractionService(db)
    try:
        return service.get_flags_for_content(content_id, content_type)
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except ItemNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))