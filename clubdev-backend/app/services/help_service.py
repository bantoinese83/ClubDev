# help_service.py

import logging
from functools import lru_cache

from sqlmodel import Session
from uuid import UUID
from ..crud import help_question, help_answer
from ..db.models import HelpQuestion, HelpAnswer
from ..db.schemas import HelpQuestionCreate, HelpAnswerCreate, HelpQuestionUpdate, HelpAnswerUpdate
from ..core.exceptions import DatabaseError, ItemNotFoundError

class HelpService:
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)

    def create_help_question(self, help_question_in: HelpQuestionCreate) -> HelpQuestion:
        try:
            return help_question.create(self.db, help_question_in)
        except Exception as e:
            self.logger.error(f"Error creating help question: {e}")
            raise DatabaseError(f"Error creating help question: {e}")

    @lru_cache(maxsize=128)
    def get_help_question(self, question_id: UUID) -> HelpQuestion:
        try:
            question = help_question.get(self.db, question_id)
            if not question:
                raise ItemNotFoundError(f"Help question with ID {question_id} not found")
            return question
        except Exception as e:
            self.logger.error(f"Error retrieving help question with ID {question_id}: {e}")
            raise DatabaseError(f"Error retrieving help question with ID {question_id}: {e}")

    def update_help_question(self, question_id: UUID, help_question_in: HelpQuestionUpdate) -> HelpQuestion:
        try:
            question = help_question.update(self.db, question_id, help_question_in)
            if not question:
                raise ItemNotFoundError(f"Help question with ID {question_id} not found")
            return question
        except Exception as e:
            self.logger.error(f"Error updating help question with ID {question_id}: {e}")
            raise DatabaseError(f"Error updating help question with ID {question_id}: {e}")

    def delete_help_question(self, question_id: UUID) -> None:
        try:
            help_question.delete(self.db, question_id)
        except Exception as e:
            self.logger.error(f"Error deleting help question with ID {question_id}: {e}")
            raise DatabaseError(f"Error deleting help question with ID {question_id}: {e}")

    def create_help_answer(self, help_answer_in: HelpAnswerCreate) -> HelpAnswer:
        try:
            return help_answer.create(self.db, help_answer_in)
        except Exception as e:
            self.logger.error(f"Error creating help answer: {e}")
            raise DatabaseError(f"Error creating help answer: {e}")

    @lru_cache(maxsize=128)
    def get_help_answer(self, answer_id: UUID) -> HelpAnswer:
        try:
            answer = help_answer.get(self.db, answer_id)
            if not answer:
                raise ItemNotFoundError(f"Help answer with ID {answer_id} not found")
            return answer
        except Exception as e:
            self.logger.error(f"Error retrieving help answer with ID {answer_id}: {e}")
            raise DatabaseError(f"Error retrieving help answer with ID {answer_id}: {e}")

    def update_help_answer(self, answer_id: UUID, help_answer_in: HelpAnswerUpdate) -> HelpAnswer:
        try:
            answer = help_answer.update(self.db, answer_id, help_answer_in)
            if not answer:
                raise ItemNotFoundError(f"Help answer with ID {answer_id} not found")
            return answer
        except Exception as e:
            self.logger.error(f"Error updating help answer with ID {answer_id}: {e}")
            raise DatabaseError(f"Error updating help answer with ID {answer_id}: {e}")

    def delete_help_answer(self, answer_id: UUID) -> None:
        try:
            help_answer.delete(self.db, answer_id)
        except Exception as e:
            self.logger.error(f"Error deleting help answer with ID {answer_id}: {e}")
            raise DatabaseError(f"Error deleting help answer with ID {answer_id}: {e}")