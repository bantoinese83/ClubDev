from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from uuid import UUID
from ...db.database import get_db
from ...db.schemas import HelpQuestionCreate, HelpAnswerCreate, HelpQuestionUpdate, HelpAnswerUpdate
from ...services.help_service import HelpService
from ...db.models import HelpQuestion, HelpAnswer
from ...core.exceptions import ItemNotFoundError, DatabaseError
import logging

help_router = APIRouter()
logger = logging.getLogger(__name__)



@help_router.post("/questions/", response_model=HelpQuestion, status_code=status.HTTP_201_CREATED, tags=["Help Questions ❓"])
def create_help_question(help_question_in: HelpQuestionCreate, db: Session = Depends(get_db)):
    help_service = HelpService(db)
    try:
        return help_service.create_help_question(help_question_in)
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected error")

@help_router.get("/questions/{question_id}", response_model=HelpQuestion, tags=["Help Questions ❓"])
def get_help_question(question_id: UUID, db: Session = Depends(get_db)):
    help_service = HelpService(db)
    try:
        return help_service.get_help_question(question_id)
    except ItemNotFoundError as e:
        logger.warning(f"Item not found: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected error")

@help_router.put("/questions/{question_id}", response_model=HelpQuestion, tags=["Help Questions ❓"])
def update_help_question(question_id: UUID, help_question_in: HelpQuestionUpdate, db: Session = Depends(get_db)):
    help_service = HelpService(db)
    try:
        return help_service.update_help_question(question_id, help_question_in)
    except ItemNotFoundError as e:
        logger.warning(f"Item not found: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected error")

@help_router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Help Questions ❓"])
def delete_help_question(question_id: UUID, db: Session = Depends(get_db)):
    help_service = HelpService(db)
    try:
        help_service.delete_help_question(question_id)
    except ItemNotFoundError as e:
        logger.warning(f"Item not found: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected error")

@help_router.post("/answers/", response_model=HelpAnswer, status_code=status.HTTP_201_CREATED, tags=["Help Answers 💬"])
def create_help_answer(help_answer_in: HelpAnswerCreate, db: Session = Depends(get_db)):
    help_service = HelpService(db)
    try:
        return help_service.create_help_answer(help_answer_in)
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected error")

@help_router.get("/answers/{answer_id}", response_model=HelpAnswer, tags=["Help Answers 💬"])
def get_help_answer(answer_id: UUID, db: Session = Depends(get_db)):
    help_service = HelpService(db)
    try:
        return help_service.get_help_answer(answer_id)
    except ItemNotFoundError as e:
        logger.warning(f"Item not found: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected error")

@help_router.put("/answers/{answer_id}", response_model=HelpAnswer, tags=["Help Answers 💬"])
def update_help_answer(answer_id: UUID, help_answer_in: HelpAnswerUpdate, db: Session = Depends(get_db)):
    help_service = HelpService(db)
    try:
        return help_service.update_help_answer(answer_id, help_answer_in)
    except ItemNotFoundError as e:
        logger.warning(f"Item not found: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected error")

@help_router.delete("/answers/{answer_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Help Answers 💬"])
def delete_help_answer(answer_id: UUID, db: Session = Depends(get_db)):
    help_service = HelpService(db)
    try:
        help_service.delete_help_answer(answer_id)
    except ItemNotFoundError as e:
        logger.warning(f"Item not found: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected error")