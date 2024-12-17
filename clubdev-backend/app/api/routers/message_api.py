from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from uuid import UUID
from ...db.database import get_db
from ...db.schemas import DirectMessageCreate, DirectMessageUpdate, DirectMessageRead
from ...services.message_service import MessageService
from ...core.exceptions import ItemNotFoundError, DatabaseError
import logging

message_router = APIRouter()
logger = logging.getLogger(__name__)

@message_router.post("/messages/", response_model=DirectMessageRead, status_code=status.HTTP_201_CREATED, tags=["Direct Messages 📩"])
def create_direct_message(message_in: DirectMessageCreate, db: Session = Depends(get_db)):
    message_service = MessageService(db)
    try:
        return message_service.create_direct_message(message_in)
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected error")

@message_router.get("/messages/{message_id}", response_model=DirectMessageRead, tags=["Direct Messages 📩"])
def get_direct_message(message_id: UUID, db: Session = Depends(get_db)):
    message_service = MessageService(db)
    try:
        return message_service.get_direct_message(message_id)
    except ItemNotFoundError as e:
        logger.warning(f"Item not found: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected error")

@message_router.put("/messages/{message_id}", response_model=DirectMessageRead, tags=["Direct Messages 📩"])
def update_direct_message(message_id: UUID, message_in: DirectMessageUpdate, db: Session = Depends(get_db)):
    message_service = MessageService(db)
    try:
        return message_service.update_direct_message(message_id, message_in)
    except ItemNotFoundError as e:
        logger.warning(f"Item not found: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected error")

@message_router.delete("/messages/{message_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Direct Messages 📩"])
def delete_direct_message(message_id: UUID, db: Session = Depends(get_db)):
    message_service = MessageService(db)
    try:
        message_service.delete_direct_message(message_id)
    except ItemNotFoundError as e:
        logger.warning(f"Item not found: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected error")