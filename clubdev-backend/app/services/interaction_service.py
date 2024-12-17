from functools import lru_cache
from typing import List
from uuid import UUID

from sqlmodel import Session, select
from ..crud import like, comment, flag
from ..db.models import Like, Comment, Flag, User
from ..db.schemas import LikeCreate, CommentCreate, CommentUpdate, FlagCreate
from ..core.exceptions import ItemNotFoundError, DatabaseError
from fastapi import HTTPException, status
import logging

class InteractionService:
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)

    def like_content(self, user_id: UUID, content_id: UUID, content_type: str) -> Like:
        try:
            like_in = LikeCreate(
                user_id=user_id,
                script_id=content_id if content_type == "script" else None,
                blog_post_id=content_id if content_type == "blog_post" else None
            )
            new_like = like.create(self.db, like_in)
            user = self.db.get(User, user_id)
            user.likes_count += 1
            self.db.commit()
            self.logger.info(f"User {user_id} liked {content_type} {content_id}")
            return new_like
        except Exception as e:
            self.logger.error(f"Error liking content: {e}")
            raise

    def unlike_content(self, user_id: UUID, content_id: UUID, content_type: str) -> None:
        try:
            statement = select(Like).where(
                Like.user_id == user_id,
                Like.script_id == content_id if content_type == "script" else None,
                Like.blog_post_id == content_id if content_type == "blog_post" else None
            )
            like_obj = self.db.exec(statement).first()
            if like_obj:
                self.db.delete(like_obj)
                user = self.db.get(User, user_id)
                user.likes_count -= 1
                self.db.commit()
                self.logger.info(f"User {user_id} unliked {content_type} {content_id}")
        except Exception as e:
            self.logger.error(f"Error unliking content: {e}")
            raise

    def comment_on_content(self, user_id: UUID, content_id: UUID, content_type: str, comment_text: str) -> Comment:
        try:
            comment_in = CommentCreate(
                user_id=user_id,
                content=comment_text,
                script_id=content_id if content_type == "script" else None,
                blog_post_id=content_id if content_type == "blog_post" else None
            )
            new_comment = comment.create(self.db, comment_in)
            user = self.db.get(User, user_id)
            user.comments_count += 1
            self.db.commit()
            self.logger.info(f"User {user_id} commented on {content_type} {content_id}")
            return new_comment
        except Exception as e:
            self.logger.error(f"Error commenting on content: {e}")
            raise

    def update_comment(self, user_id: UUID, comment_id: UUID, comment_text: str) -> Comment:
        try:
            comment_in = CommentUpdate(content=comment_text)
            updated_comment = comment.update(self.db, comment_id, comment_in)
            self.logger.info(f"User {user_id} updated comment {comment_id}")
            return updated_comment
        except ItemNotFoundError as e:
            self.logger.error(f"Comment with ID {comment_id} not found: {e}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
        except DatabaseError as e:
            self.logger.error(f"Database error updating comment {comment_id}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
        except Exception as e:
            self.logger.error(f"Unexpected error updating comment {comment_id}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected error")

    def delete_comment(self, user_id: UUID, comment_id: UUID) -> None:
        try:
            comment.delete(self.db, comment_id)
            user = self.db.get(User, user_id)
            user.comments_count -= 1
            self.db.commit()
            self.logger.info(f"User {user_id} deleted comment {comment_id}")
        except ItemNotFoundError as e:
            self.logger.error(f"Comment with ID {comment_id} not found: {e}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
        except DatabaseError as e:
            self.logger.error(f"Database error deleting comment {comment_id}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
        except Exception as e:
            self.logger.error(f"Unexpected error deleting comment {comment_id}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected error")

    def flag_content(self, user_id: UUID, content_id: UUID, content_type: str, reason: str) -> Flag:
        try:
            flag_in = FlagCreate(
                user_id=user_id,
                flagger_id=user_id,
                script_id=content_id if content_type == "script" else None,
                blog_post_id=content_id if content_type == "blog_post" else None,
                reason=reason
            )
            new_flag = flag.create(self.db, flag_in)
            user = self.db.get(User, user_id)
            user.flags_count += 1
            self.db.commit()
            self.logger.info(f"User {user_id} flagged {content_type} {content_id} for {reason}")
            return new_flag
        except Exception as e:
            self.logger.error(f"Error flagging content: {e}")
            raise

    @lru_cache(maxsize=128)
    def get_likes_for_content(self, content_id: UUID, content_type: str) -> List[Like]:
        try:
            statement = select(Like).where(
                Like.script_id == content_id if content_type == "script" else None,
                Like.blog_post_id == content_id if content_type == "blog_post" else None
            )
            likes = self.db.exec(statement).all()
            self.logger.info(f"Retrieved likes for {content_type} {content_id}")
            return likes
        except Exception as e:
            self.logger.error(f"Error retrieving likes for content: {e}")
            raise

    @lru_cache(maxsize=128)
    def get_comments_for_content(self, content_id: UUID, content_type: str) -> List[Comment]:
        try:
            statement = select(Comment).where(
                Comment.script_id == content_id if content_type == "script" else None,
                Comment.blog_post_id == content_id if content_type == "blog_post" else None
            )
            comments = self.db.exec(statement).all()
            self.logger.info(f"Retrieved comments for {content_type} {content_id}")
            return comments
        except Exception as e:
            self.logger.error(f"Error retrieving comments for content: {e}")
            raise

    @lru_cache(maxsize=128)
    def get_flags_for_content(self, content_id: UUID, content_type: str) -> List[Flag]:
        try:
            statement = select(Flag).where(
                Flag.script_id == content_id if content_type == "script" else None,
                Flag.blog_post_id == content_id if content_type == "blog_post" else None
            )
            flags = self.db.exec(statement).all()
            self.logger.info(f"Retrieved flags for {content_type} {content_id}")
            return flags
        except Exception as e:
            self.logger.error(f"Error retrieving flags for content: {e}")
            raise