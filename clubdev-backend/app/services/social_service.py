# social_service.py
from functools import lru_cache

from sqlmodel import Session, select
from uuid import UUID
from ..db.models import Follow, User
from ..core.exceptions import DatabaseError, ItemNotFoundError

class SocialService:
    def __init__(self, db: Session):
        self.db = db

    def get_user(self, user_id: UUID) -> User:
        try:
            statement = select(User).where(User.id == user_id)
            user = self.db.exec(statement).first()
            if not user:
                raise ItemNotFoundError(f"User with ID {user_id} not found")
            return user
        except Exception as e:
            raise DatabaseError(f"Error retrieving user: {e}")

    def follow_user(self, follower_id: UUID, followed_id: UUID) -> Follow:
        try:
            follower = self.get_user(follower_id)
            followed = self.get_user(followed_id)

            follow = Follow(follower_id=follower_id, followed_id=followed_id)
            self.db.add(follow)
            self.db.commit()
            self.db.refresh(follow)

            follower.following_count += 1
            followed.followers_count += 1
            self.db.add(follower)
            self.db.add(followed)
            self.db.commit()

            return follow
        except Exception as e:
            raise DatabaseError(f"Error following user: {e}")

    def unfollow_user(self, follower_id: UUID, followed_id: UUID) -> None:
        try:
            statement = select(Follow).where(Follow.follower_id == follower_id, Follow.followed_id == followed_id)
            follow = self.db.exec(statement).first()
            if follow:
                self.db.delete(follow)
                self.db.commit()

                follower = self.get_user(follower_id)
                followed = self.get_user(followed_id)
                follower.following_count -= 1
                followed.followers_count -= 1
                self.db.add(follower)
                self.db.add(followed)
                self.db.commit()
        except Exception as e:
            raise DatabaseError(f"Error unfollowing user: {e}")

    @lru_cache(maxsize=128)
    def get_followers(self, user_id: UUID):
        try:
            statement = select(Follow).where(Follow.followed_id == user_id)
            follows = self.db.exec(statement).all()
            return [self.get_user(f.follower_id) for f in follows]
        except Exception as e:
            raise DatabaseError(f"Error getting followers: {e}")

    @lru_cache(maxsize=128)
    def get_following(self, user_id: UUID):
        try:
            statement = select(Follow).where(Follow.follower_id == user_id)
            follows = self.db.exec(statement).all()
            return [self.get_user(f.followed_id) for f in follows]
        except Exception as e:
            raise DatabaseError(f"Error getting following: {e}")