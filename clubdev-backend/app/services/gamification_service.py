import logging
from datetime import datetime, timedelta
from typing import Type, Optional, Sequence, Dict, Any
from uuid import UUID
from functools import lru_cache

from sqlalchemy import func, desc, and_
from sqlmodel import Session, select, SQLModel, Field, asc

from ..core.config import thresholds
from ..core.exceptions import DatabaseError, ItemNotFoundError
from ..db.models import Script, Like, Trophy, Challenge, Flag, HelpAnswer, BlogPost, Achievement, Badge, \
    UserAchievement, UserBadge, GamificationEvent, Leaderboard, DailyChallenge, User


class GamificationService:

    def __init__(self, db: Session):
        self.db = db
        self.thresholds = thresholds

    def _get_count(self, model: Type[SQLModel], user_id: UUID, filter_condition: Optional[bool] = None) -> int:
        """Get count of items for a user with an optional filter condition."""
        try:
            statement = select(func.count(model.id)).where(model.author_id == user_id)
            if filter_condition:
                statement = statement.where(filter_condition)
            result = self.db.exec(statement).one()
            return result[0]
        except Exception as e:
            raise DatabaseError(f"Error getting count for {model.__name__}: {e}")

    def _get_sum(self, model: Type[SQLModel], user_id: UUID, column: Field) -> int:
        """Get sum of a column for a user."""
        try:
            statement = select(func.sum(column)).where(model.author_id == user_id)
            result = self.db.exec(statement).one()
            return result[0]
        except Exception as e:
            raise DatabaseError(f"Error getting sum for {model.__name__}: {e}")

    def _award_item(self, item_model: Type[SQLModel], user_id: UUID, name: str) -> SQLModel:
        """Award an item to a user."""
        try:
            item = item_model(name=name, user_id=user_id)
            self.db.add(item)
            self.db.commit()
            self.db.refresh(item)
            return item
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(f"Error awarding item {item_model.__name__}: {e}")

    def _get_item(self, item_model: Type[SQLModel], item_id: UUID) -> SQLModel:
        """Get an item by ID."""
        try:
            item = self.db.get(item_model, item_id)
            if not item:
                raise ItemNotFoundError(f"{item_model.__name__} with ID {item_id} not found")
            return item
        except Exception as e:
            raise DatabaseError(f"Error getting item {item_model.__name__}: {e}")

    def _update_item(self, item_model: Type[SQLModel], item_id: UUID, item_in: dict) -> SQLModel:
        """Update an item by ID."""
        try:
            item = self._get_item(item_model, item_id)
            for key, value in item_in.items():
                setattr(item, key, value)
            self.db.commit()
            self.db.refresh(item)
            return item
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(f"Error updating item {item_model.__name__}: {e}")

    def _delete_item(self, item_model: Type[SQLModel], item_id: UUID) -> None:
        """Delete an item by ID."""
        try:
            item = self._get_item(item_model, item_id)
            self.db.delete(item)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(f"Error deleting item {item_model.__name__}: {e}")

    def get_items(self, item_model: Type[SQLModel], limit: int = 10, offset: int = 0,
                  filters: Optional[Dict[str, Any]] = None, sort_by: Optional[str] = None, sort_order: str = "asc") -> \
    Sequence[SQLModel]:
        """Get a list of items with pagination, filtering, and sorting."""
        try:
            statement = select(item_model)
            if filters:
                for attr, value in filters.items():
                    statement = statement.where(getattr(item_model, attr) == value)
            if sort_by:
                order = desc if sort_order == "desc" else asc
                statement = statement.order_by(order(getattr(item_model, sort_by)))
            statement = statement.limit(limit).offset(offset)
            items = self.db.exec(statement).all()
            return items
        except Exception as e:
            raise DatabaseError(f"Error getting items {item_model.__name__}: {e}")

    def check_and_award_trophies_and_challenges(self, user_id: UUID):
        """Check and award trophies and challenges to a user based on their activities."""
        try:
            script_count = self._get_count(Script, user_id)
            syntax_sorcerer_count = self._get_count(Script, user_id, Script.is_syntax_sorcerer == True)
            innovator_count = self._get_count(Script, user_id, Script.is_innovative == True)
            trailblazer_count = self._get_count(Script, user_id, Script.is_trailblazing == True)
            collaborator_count = self._get_count(Script, user_id, Script.is_collaborative == True)
            like_count_on_scripts = self._get_count(Like, user_id, Script.author_id == user_id)
            view_sum = self._get_sum(Script, user_id, Script.views)
            flag_count = self._get_count(Flag, user_id)
            help_answer_count = self._get_count(HelpAnswer, user_id)
            blog_post_count = self._get_count(BlogPost, user_id)
            like_count_on_posts = self._get_count(Like, user_id, BlogPost.author_id == user_id)
            statement = select(func.count(func.distinct(Script.language))).where(Script.author_id == user_id)
            cross_language_count = self.db.exec(statement).one()[0]

            trophies_to_award = []
            challenges_to_award = []
            now = datetime.now()
            start_of_week = now - timedelta(days=now.weekday())
            start_of_month = now.replace(day=1)

            if script_count >= self.thresholds["ROOKIE_CONTRIBUTOR_THRESHOLD"]:
                trophies_to_award.append("Rookie Contributor")
            if syntax_sorcerer_count >= self.thresholds["SYNTAX_SORCERER_THRESHOLD"]:
                trophies_to_award.append("Syntax Sorcerer")
            if cross_language_count >= self.thresholds["CROSS_LANGUAGE_WIZARD_THRESHOLD"]:
                trophies_to_award.append("Cross-Language Wizard")
            if like_count_on_scripts >= self.thresholds["POPULAR_CREATOR_THRESHOLD"]:
                trophies_to_award.append("Popular Creator")
            if view_sum >= self.thresholds["MASTERMIND_THRESHOLD"]:
                trophies_to_award.append("Mastermind")
            if self._get_count(Like, user_id) >= self.thresholds["REVIEWER_THRESHOLD"]:
                trophies_to_award.append("Reviewer")
            if self.is_trending_script_of_the_week(user_id):
                trophies_to_award.append("Trendsetter")
            if flag_count >= self.thresholds["BUG_HUNTER_THRESHOLD"]:
                trophies_to_award.append("Bug Hunter")
            if help_answer_count >= self.thresholds["HELPER_THRESHOLD"]:
                trophies_to_award.append("Helper")
            if self.is_top_coder_of_the_month(user_id):
                trophies_to_award.append("Top Coder")
            if blog_post_count >= self.thresholds["BLOG_WRITER_THRESHOLD"]:
                trophies_to_award.append("Blog Writer")
            if like_count_on_posts >= self.thresholds["POPULAR_BLOGGER_THRESHOLD"]:
                trophies_to_award.append("Popular Blogger")
            if blog_post_count >= self.thresholds["PROLIFIC_BLOGGER_THRESHOLD"]:
                trophies_to_award.append("Prolific Blogger")
            if like_count_on_posts >= self.thresholds["BLOG_INFLUENCER_THRESHOLD"]:
                trophies_to_award.append("Blog Influencer")
            if script_count >= self.thresholds["BRONZE_THRESHOLD"]:
                trophies_to_award.append("Bronze Trophy")
            if script_count >= self.thresholds["SILVER_THRESHOLD"]:
                trophies_to_award.append("Silver Trophy")
            if script_count >= self.thresholds["GOLD_THRESHOLD"]:
                trophies_to_award.append("Gold Trophy")
            if syntax_sorcerer_count >= self.thresholds["POLYMATH_THRESHOLD"]:
                trophies_to_award.append("Polymath Trophy")
            if innovator_count >= self.thresholds["INNOVATOR_THRESHOLD"]:
                trophies_to_award.append("Innovator Trophy")
            if trailblazer_count >= self.thresholds["TRAILBLAZER_THRESHOLD"]:
                trophies_to_award.append("Trailblazer Trophy")
            if collaborator_count >= self.thresholds["COLLABORATOR_THRESHOLD"]:
                trophies_to_award.append("Collaborator Trophy")

            daily_upload_count = self._get_count(Script, user_id, func.date(Script.created_at) == func.current_date())
            weekly_upvoter_count = self._get_count(Like, user_id, and_(
                func.date_trunc('week', Script.created_at) == func.date_trunc('week', func.current_date())))
            pythonista_count = self._get_count(Script, user_id, and_(
                Script.language == "Python",
                func.date_trunc('week', Script.created_at) == func.date_trunc('week', func.current_date())
            ))
            blog_post_week_count = self._get_count(BlogPost, user_id, and_(
                func.date_trunc('week', BlogPost.created_at) == func.date_trunc('week', func.current_date())
            ))
            blog_post_month_count = self._get_count(BlogPost, user_id, and_(
                func.date_trunc('month', BlogPost.created_at) == func.date_trunc('month', func.current_date())
            ))
            like_count_on_posts = self._get_count(Like, user_id, and_(
                func.date_trunc('month', BlogPost.created_at) == func.date_trunc('month', func.current_date())
            ))

            if daily_upload_count >= self.thresholds["DAILY_UPLOAD_THRESHOLD"]:
                challenges_to_award.append(("Daily Upload", "100 bonus XP"))
            if weekly_upvoter_count >= self.thresholds["WEEKLY_UPVOTER_THRESHOLD"]:
                challenges_to_award.append(("Weekly Upvoter", "Reviewer badge"))
            if pythonista_count >= 1:
                challenges_to_award.append(("Pythonista", "Pythonista badge"))
            if blog_post_week_count >= 1:
                challenges_to_award.append(("Blogger", "Blogger badge"))
            if blog_post_month_count >= self.thresholds["PROLIFIC_BLOGGER_MONTH_THRESHOLD"]:
                challenges_to_award.append(("Prolific Blogger", "Prolific Blogger badge"))
            if like_count_on_posts >= self.thresholds["BLOG_INFLUENCER_MONTH_THRESHOLD"]:
                challenges_to_award.append(("Blog Influencer", "Blog Influencer badge"))

            # Add trophies and challenges in a batch
            trophies = [Trophy(name=trophy_name, user_id=user_id) for trophy_name in trophies_to_award]
            challenges = [Challenge(name=name, user_id=user_id, reward=reward) for name, reward in challenges_to_award]
            self.db.add_all(trophies + challenges)
            self.db.commit()
            for trophy in trophies:
                self.db.refresh(trophy)
            for challenge in challenges:
                self.db.refresh(challenge)

            # Update user counts
            user = self._get_item(User, user_id)
            user.trophies_count += len(trophies_to_award)
            user.challenges_count += len(challenges_to_award)
            self.db.commit()
            self.db.refresh(user)
        except Exception as e:
            raise DatabaseError(f"Error checking and awarding trophies and challenges: {e}")

    def award_trophy(self, user_id: UUID, trophy_name: str) -> Trophy:
        """Award a specific trophy to a user."""
        return self._award_item(Trophy, user_id, trophy_name)

    def is_trending_script_of_the_week(self, user_id: UUID) -> bool:
        """Check if a user's script is trending for the week."""
        try:
            now = datetime.now()
            start_of_week = now - timedelta(days=now.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            statement = select(Script).where(
                Script.author_id == user_id,
                Script.created_at >= start_of_week,
                Script.created_at <= end_of_week
            ).order_by(desc(Script.views))
            return self.db.exec(statement).first() is not None
        except Exception as e:
            raise DatabaseError(f"Error checking trending script of the week: {e}")

    def is_top_coder_of_the_month(self, user_id: UUID) -> bool:
        """Check if a user is the top coder of the month."""
        try:
            now = datetime.now()
            start_of_month = now.replace(day=1)
            end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            statement = select(Script).where(
                Script.author_id == user_id,
                Script.created_at >= start_of_month,
                Script.created_at <= end_of_month
            ).order_by(desc(Script.likes))
            return self.db.exec(statement).first() is not None
        except Exception as e:
            raise DatabaseError(f"Error checking top coder of the month: {e}")

    @lru_cache(maxsize=128)
    def get_achievement(self, achievement_id: UUID) -> Achievement:
        """Get an achievement by ID."""
        return self._get_item(Achievement, achievement_id)

    def update_achievement(self, achievement_id: UUID, achievement_in: dict) -> Achievement:
        """Update an achievement by ID."""
        return self._update_item(Achievement, achievement_id, achievement_in)

    def delete_achievement(self, achievement_id: UUID) -> None:
        """Delete an achievement by ID."""
        return self._delete_item(Achievement, achievement_id)

    @lru_cache(maxsize=128)
    def get_badge(self, badge_id: UUID) -> Badge:
        """Get a badge by ID."""
        return self._get_item(Badge, badge_id)

    def update_badge(self, badge_id: UUID, badge_in: dict) -> Badge:
        """Update a badge by ID."""
        return self._update_item(Badge, badge_id, badge_in)

    def delete_badge(self, badge_id: UUID) -> None:
        """Delete a badge by ID."""
        return self._delete_item(Badge, badge_id)

    @lru_cache(maxsize=128)
    def get_trophy(self, trophy_id: UUID) -> Trophy:
        """Get a trophy by ID."""
        return self._get_item(Trophy, trophy_id)

    def update_trophy(self, trophy_id: UUID, trophy_in: dict) -> Trophy:
        """Update a trophy by ID."""
        return self._update_item(Trophy, trophy_id, trophy_in)

    def delete_trophy(self, trophy_id: UUID) -> None:
        """Delete a trophy by ID."""
        return self._delete_item(Trophy, trophy_id)

    @lru_cache(maxsize=128)
    def get_user_achievement(self, user_achievement_id: UUID) -> UserAchievement:
        """Get a user achievement by ID."""
        return self._get_item(UserAchievement, user_achievement_id)

    def update_user_achievement(self, user_achievement_id: UUID, user_achievement_in: dict) -> UserAchievement:
        """Update a user achievement by ID."""
        return self._update_item(UserAchievement, user_achievement_id, user_achievement_in)

    def delete_user_achievement(self, user_achievement_id: UUID) -> None:
        """Delete a user achievement by ID."""
        return self._delete_item(UserAchievement, user_achievement_id)

    @lru_cache(maxsize=128)
    def get_user_badge(self, user_badge_id: UUID) -> UserBadge:
        """Get a user badge by ID."""
        return self._get_item(UserBadge, user_badge_id)

    def update_user_badge(self, user_badge_id: UUID, user_badge_in: dict) -> UserBadge:
        """Update a user badge by ID."""
        return self._update_item(UserBadge, user_badge_id, user_badge_in)

    def delete_user_badge(self, user_badge_id: UUID) -> None:
        """Delete a user badge by ID."""
        return self._delete_item(UserBadge, user_badge_id)

    @lru_cache(maxsize=128)
    def get_gamification_event(self, gamification_event_id: UUID) -> GamificationEvent:
        """Get a gamification event by ID."""
        return self._get_item(GamificationEvent, gamification_event_id)

    def update_gamification_event(self, gamification_event_id: UUID, gamification_event_in: dict) -> GamificationEvent:
        """Update a gamification event by ID."""
        return self._update_item(GamificationEvent, gamification_event_id, gamification_event_in)

    def delete_gamification_event(self, gamification_event_id: UUID) -> None:
        """Delete a gamification event by ID."""
        return self._delete_item(GamificationEvent, gamification_event_id)

    @lru_cache(maxsize=128)
    def get_leaderboard(self, leaderboard_id: UUID) -> Leaderboard:
        """Get a leaderboard by ID."""
        return self._get_item(Leaderboard, leaderboard_id)

    def update_leaderboard(self, leaderboard_id: UUID, leaderboard_in: dict) -> Leaderboard:
        """Update a leaderboard by ID."""
        return self._update_item(Leaderboard, leaderboard_id, leaderboard_in)

    def delete_leaderboard(self, leaderboard_id: UUID) -> None:
        """Delete a leaderboard by ID."""
        return self._delete_item(Leaderboard, leaderboard_id)

    @lru_cache(maxsize=128)
    def get_daily_challenge(self, daily_challenge_id: UUID) -> Optional[DailyChallenge]:
        """Get a daily challenge by ID."""
        logging.info(f"Fetching DailyChallenge with ID: {daily_challenge_id}")
        return self._get_item(DailyChallenge, daily_challenge_id)

    def update_daily_challenge(self, daily_challenge_id: UUID, daily_challenge_in: dict) -> DailyChallenge:
        """Update a daily challenge by ID."""
        return self._update_item(DailyChallenge, daily_challenge_id, daily_challenge_in)

    def delete_daily_challenge(self, daily_challenge_id: UUID) -> None:
        """Delete a daily challenge by ID."""
        return self._delete_item(DailyChallenge, daily_challenge_id)

    @lru_cache(maxsize=128)
    def get_challenge(self, challenge_id: UUID) -> Challenge:
        """Get a challenge by ID."""
        return self._get_item(Challenge, challenge_id)

    def update_challenge(self, challenge_id: UUID, challenge_in: dict) -> Challenge:
        """Update a challenge by ID."""
        return self._update_item(Challenge, challenge_id, challenge_in)

    def delete_challenge(self, challenge_id: UUID) -> None:
        """Delete a challenge by ID."""
        return self._delete_item(Challenge, challenge_id)

    def award_user_badge(self, user_id: UUID, badge_id: UUID) -> UserBadge:
        """Award a badge to a user."""
        user_badge = UserBadge(user_id=user_id, badge_id=badge_id)
        self.db.add(user_badge)
        user = self.db.get(User, user_id)
        user.user_badges_count += 1
        self.db.commit()
        self.db.refresh(user_badge)
        return user_badge

    def award_user_achievement(self, user_id: UUID, achievement_id: UUID) -> UserAchievement:
        """Award an achievement to a user."""
        user_achievement = UserAchievement(user_id=user_id, achievement_id=achievement_id)
        self.db.add(user_achievement)
        user = self.db.get(User, user_id)
        user.user_achievements_count += 1
        self.db.commit()
        self.db.refresh(user_achievement)
        return user_achievement

    def award_challenge(self, user_id: UUID, challenge_id: UUID) -> Challenge:
        """Award a challenge to a user."""
        challenge = Challenge(user_id=user_id, challenge_id=challenge_id)
        self.db.add(challenge)
        user = self.db.get(User, user_id)
        user.challenges_count += 1
        self.db.commit()
        self.db.refresh(challenge)
        return challenge
