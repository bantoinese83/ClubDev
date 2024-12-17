# user_service.py
import logging
from functools import lru_cache
from typing import Sequence, List
import uuid

from fastapi import HTTPException, status, UploadFile
from sqlmodel import Session, select

from ..crud import user
from ..db.models import User, UserProfile
from ..db.schemas import UserUpdate, UserProfileCreate
from ..utils.s3_util import S3Util

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, db: Session, s3_util: S3Util):
        self.db = db
        self.s3_util = s3_util

    @lru_cache(maxsize=128)
    def get_user(self, user_id: uuid.UUID) -> User:
        try:
            user_obj = user.get(self.db, user_id)
            if not user_obj:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )
            return user_obj
        except Exception as e:
            logger.error(f"Error retrieving user with ID {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving user",
            )

    def update_user_profile(self, user_id: uuid.UUID, avatar: UploadFile) -> UserProfile:
        try:
            statement = select(UserProfile).where(UserProfile.user_id == user_id)
            user_profile = self.db.exec(statement).first()
            if not user_profile:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User profile not found",
                )

            if user_profile.avatar_url:
                self.s3_util.delete_file(user_profile.avatar_url)

            avatar_url = self.s3_util.upload_file(avatar, "avatars")
            user_profile.avatar_url = avatar_url
            self.db.commit()
            self.db.refresh(user_profile)
            logger.info(f"User profile for user ID {user_id} updated successfully.")
            return user_profile
        except Exception as e:
            logger.error(f"Error updating user profile for user ID {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error updating user profile",
            )

    def delete_user(self, user_id: uuid.UUID) -> None:
        try:
            user.delete(self.db, user_id)
            logger.info(f"User with ID {user_id} deleted successfully.")
        except Exception as e:
            logger.error(f"Error deleting user with ID {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error deleting user",
            )

    @lru_cache(maxsize=128)
    def get_user_by_email(self, email: str) -> User:
        try:
            statement = select(User).where(User.email == email)
            user_obj = self.db.exec(statement).first()
            if not user_obj:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )
            return user_obj
        except Exception as e:
            logger.error(f"Error retrieving user with email {email}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving user",
            )

    @lru_cache(maxsize=128)
    def get_user_by_username(self, username: str) -> User:
        try:
            statement = select(User).where(User.username == username)
            user_obj = self.db.exec(statement).first()
            if not user_obj:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )
            return user_obj
        except Exception as e:
            logger.error(f"Error retrieving user with username {username}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving user",
            )

    def update_user(self, user_id: uuid.UUID, user_in: UserUpdate) -> User:
        try:
            updated_user = user.update(self.db, user_id, user_in)
            if not updated_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )
            logger.info(f"User with ID {user_id} updated successfully.")
            return updated_user
        except Exception as e:
            logger.error(f"Error updating user with ID {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error updating user",
            )

    @lru_cache(maxsize=128)
    def get_all_users(self) -> Sequence[User]:
        try:
            users = user.get_all(self.db)
            logger.info("Retrieved all users successfully.")
            return users
        except Exception as e:
            logger.error(f"Error retrieving all users: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving users",
            )

    def count_users(self) -> int:
        try:
            count = user.count(self.db)
            logger.info(f"Counted {count} users.")
            return count
        except Exception as e:
            logger.error(f"Error counting users: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error counting users",
            )

    def deactivate_user(self, user_id: uuid.UUID) -> User:
        try:
            user_obj = self.get_user(user_id)
            user_obj.is_active = False
            self.db.commit()
            self.db.refresh(user_obj)
            logger.info(f"User with ID {user_id} deactivated successfully.")
            return user_obj
        except Exception as e:
            logger.error(f"Error deactivating user with ID {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error deactivating user",
            )

    def activate_user(self, user_id: uuid.UUID) -> User:
        try:
            user_obj = self.get_user(user_id)
            user_obj.is_active = True
            self.db.commit()
            self.db.refresh(user_obj)
            logger.info(f"User with ID {user_id} activated successfully.")
            return user_obj
        except Exception as e:
            logger.error(f"Error activating user with ID {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error activating user",
            )

    @lru_cache(maxsize=128)
    def get_users_by_auth_provider(self, auth_provider: str) -> List[User]:
        try:
            users = user.get_by_field(self.db, "auth_provider", auth_provider)
            logger.info(
                f"Retrieved users with auth provider {auth_provider} successfully."
            )
            return users
        except Exception as e:
            logger.error(
                f"Error retrieving users with auth provider {auth_provider}: {e}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving users",
            )

    @lru_cache(maxsize=128)
    def get_users_by_active_status(self, is_active: bool) -> List[User]:
        try:
            users = user.get_by_field(self.db, "is_active", is_active)
            logger.info(f"Retrieved users with active status {is_active} successfully.")
            return users
        except Exception as e:
            logger.error(f"Error retrieving users with active status {is_active}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving users",
            )

    def create_user_profile(self, user_id: uuid.UUID, user_profile: UserProfileCreate) -> UserProfile:
        try:
            user_profile_obj = UserProfile(user_id=user_id, **user_profile.model_dump())
            self.db.add(user_profile_obj)
            self.db.commit()
            self.db.refresh(user_profile_obj)
            logger.info(f"User profile for user ID {user_id} created.")
            return user_profile_obj
        except Exception as e:
            logger.error(f"Error creating user profile for user ID {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating user profile",
            )

    @lru_cache(maxsize=128)
    def get_user_profile(self, user_id: uuid.UUID) -> UserProfile:
        try:
            statement = select(UserProfile).where(UserProfile.user_id == user_id)
            user_profile = self.db.exec(statement).first()
            if not user_profile:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User profile not found",
                )
            return user_profile
        except Exception as e:
            logger.error(f"Error retrieving user profile for user ID {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving user profile",
            )