import logging
from typing import Type, TypeVar, Generic, Optional, Sequence, Any

from sqlalchemy.engine.result import Row, RowMapping
from sqlalchemy.sql import select, func
from sqlmodel import Session

from ..db.models import User, Script, BlogPost, UserProfile, UserSettings, Like, Comment, Flag, Achievement, Badge, \
    Trophy, UserAchievement, UserBadge, GamificationEvent, Leaderboard, DailyChallenge, Challenge, Follow, Message, \
    Notification, Activity, Subscription, SubscriptionPlan, Transaction, HelpQuestion, HelpAnswer, GitHubRepo, \
    AdminAction

# Set up logging
logger = logging.getLogger(__name__)

# Type variable for models
T = TypeVar("T")


class BaseCRUD(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model

    def create(self, db: Session, obj_in: T) -> T:
        try:
            db_obj = self.model(**obj_in.model_dump())
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            logger.info(f"Created {self.model.__name__} with ID {db_obj.id}")
            return db_obj
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating {self.model.__name__}: {e}")
            raise

    def get(self, db: Session, id: int) -> Optional[T]:
        try:
            db_obj = db.get(self.model, id)
            if db_obj:
                logger.info(f"Retrieved {self.model.__name__} with ID {id}")
            else:
                logger.warning(f"{self.model.__name__} with ID {id} not found")
            return db_obj
        except Exception as e:
            logger.error(f"Error retrieving {self.model.__name__} with ID {id}: {e}")
            raise

    def update(self, db: Session, id: int, obj_in: T) -> Optional[T]:
        try:
            db_obj = self.get(db, id)
            if not db_obj:
                logger.warning(f"{self.model.__name__} with ID {id} not found")
                return None
            for key, value in obj_in.model_dump(exclude_unset=True).items():
                setattr(db_obj, key, value)
            db.commit()
            db.refresh(db_obj)
            logger.info(f"Updated {self.model.__name__} with ID {id}")
            return db_obj
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating {self.model.__name__} with ID {id}: {e}")
            raise

    def delete(self, db: Session, id: int) -> None:
        try:
            db_obj = self.get(db, id)
            if db_obj:
                db.delete(db_obj)
                db.commit()
                logger.info(f"Deleted {self.model.__name__} with ID {id}")
            else:
                logger.warning(f"{self.model.__name__} with ID {id} not found")
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting {self.model.__name__} with ID {id}: {e}")
            raise

    def get_all(self, db: Session) -> Sequence[Row[Any] | RowMapping | Any]:
        try:
            statement = select(self.model)
            db_objs = db.exec(statement).all()
            logger.info(f"Retrieved all {self.model.__name__} records")
            return db_objs
        except Exception as e:
            logger.error(f"Error retrieving all {self.model.__name__} records: {e}")
            raise

    def get_by_field(self, db: Session, field: str, value: any) -> Sequence[Row[Any] | RowMapping | Any]:
        try:
            statement = select(self.model).where(getattr(self.model, field) == value)
            db_objs = db.exec(statement).all()
            logger.info(
                f"Retrieved {self.model.__name__} records where {field}={value}"
            )
            return db_objs
        except Exception as e:
            logger.error(
                f"Error retrieving {self.model.__name__} records where {field}={value}: {e}"
            )
            raise

    def count(self, db: Session) -> int:
        try:
            statement = select(func.count()).select_from(self.model)
            count = db.exec(statement).one()
            logger.info(f"Counted {count} {self.model.__name__} records")
            return count
        except Exception as e:
            logger.error(f"Error counting {self.model.__name__} records: {e}")
            raise


# User Management
class UserCRUD(BaseCRUD[User]):
    """User-related CRUD operations"""


# Content Management
class ContentCRUD(BaseCRUD[T]):
    """Content-related CRUD operations"""


# Interaction Management
class InteractionCRUD(BaseCRUD[T]):
    """User interaction CRUD operations"""


# Gamification Management
class GamificationCRUD(BaseCRUD[T]):
    """Gamification-related CRUD operations"""


# Social Management
class SocialCRUD(BaseCRUD[T]):
    """Social features CRUD operations"""


# Subscription Management
class SubscriptionCRUD(BaseCRUD[T]):
    """Subscription and payment CRUD operations"""


# Help System Management
class HelpSystemCRUD(BaseCRUD[T]):
    """Help system CRUD operations"""


# Initialize CRUD instances
user = UserCRUD(User)
user_profile = UserCRUD(UserProfile)
user_settings = UserCRUD(UserSettings)

script = ContentCRUD(Script)
blog_post = ContentCRUD(BlogPost)

like = InteractionCRUD(Like)
comment = InteractionCRUD(Comment)
flag = InteractionCRUD(Flag)

achievement = GamificationCRUD(Achievement)
badge = GamificationCRUD(Badge)
trophy = GamificationCRUD(Trophy)
user_achievement = GamificationCRUD(UserAchievement)
user_badge = GamificationCRUD(UserBadge)
gamification_event = GamificationCRUD(GamificationEvent)
leaderboard = GamificationCRUD(Leaderboard)
daily_challenge = GamificationCRUD(DailyChallenge)
challenge = GamificationCRUD(Challenge)

follow = SocialCRUD(Follow)
message = SocialCRUD(Message)
notification = SocialCRUD(Notification)
activity = SocialCRUD(Activity)

subscription = SubscriptionCRUD(Subscription)
subscription_plan = SubscriptionCRUD(SubscriptionPlan)
transaction = SubscriptionCRUD(Transaction)

help_question = HelpSystemCRUD(HelpQuestion)
help_answer = HelpSystemCRUD(HelpAnswer)

github_repo = ContentCRUD(GitHubRepo)
admin_action = UserCRUD(AdminAction)
