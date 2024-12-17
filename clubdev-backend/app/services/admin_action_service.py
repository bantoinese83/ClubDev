# admin_action_service.py

import logging
from functools import lru_cache

from sqlmodel import Session
from uuid import UUID
from fastapi import HTTPException, status
from ..crud import admin_action
from ..db.models import AdminAction
from ..db.schemas import AdminActionCreate, AdminActionUpdate
from ..core.exceptions import DatabaseError, ItemNotFoundError

logger = logging.getLogger(__name__)

class AdminActionService:
    def __init__(self, db: Session):
        self.db = db

    def create_admin_action(self, admin_action_in: AdminActionCreate) -> AdminAction:
        try:
            new_admin_action = admin_action.create(self.db, admin_action_in)
            logger.info(f"Admin action created with ID: {new_admin_action.id}")
            return new_admin_action
        except Exception as e:
            logger.error(f"Error creating admin action: {e}")
            raise DatabaseError("Error creating admin action")

    @lru_cache(maxsize=128)
    def get_admin_action(self, admin_action_id: UUID) -> AdminAction:
        try:
            admin_action_obj = admin_action.get(self.db, admin_action_id)
            if not admin_action_obj:
                raise ItemNotFoundError(f"Admin action with ID {admin_action_id} not found")
            return admin_action_obj
        except ItemNotFoundError as e:
            logger.warning(e)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except Exception as e:
            logger.error(f"Error retrieving admin action: {e}")
            raise DatabaseError("Error retrieving admin action")

    def update_admin_action(self, admin_action_id: UUID, admin_action_in: AdminActionUpdate) -> AdminAction:
        try:
            updated_admin_action = admin_action.update(self.db, admin_action_id, admin_action_in)
            if not updated_admin_action:
                raise ItemNotFoundError(f"Admin action with ID {admin_action_id} not found")
            logger.info(f"Admin action with ID {admin_action_id} updated successfully")
            return updated_admin_action
        except ItemNotFoundError as e:
            logger.warning(e)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except Exception as e:
            logger.error(f"Error updating admin action: {e}")
            raise DatabaseError("Error updating admin action")

    def delete_admin_action(self, admin_action_id: UUID) -> None:
        try:
            result = admin_action.delete(self.db, admin_action_id)
            if not result:
                raise ItemNotFoundError(f"Admin action with ID {admin_action_id} not found")
            logger.info(f"Admin action with ID {admin_action_id} deleted successfully")
        except ItemNotFoundError as e:
            logger.warning(e)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except Exception as e:
            logger.error(f"Error deleting admin action: {e}")
            raise DatabaseError("Error deleting admin action")