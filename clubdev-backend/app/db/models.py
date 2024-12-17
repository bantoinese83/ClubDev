import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, List

from sqlalchemy import JSON
from sqlmodel import SQLModel, Field, Relationship, Index, Column


# Enums
class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"
    GUEST = "guest"
    SUPER_ADMIN = "super_admin"


class TrophyLevel(str, Enum):
    BRONZE = "Bronze"
    SILVER = "Silver"
    GOLD = "Gold"


class BadgeType(str, Enum):
    ACHIEVEMENT = "Achievement"
    PARTICIPATION = "Participation"
    SPECIAL = "Special"
    COMMUNITY = "Community"


class AuthProvider(str, Enum):
    GOOGLE = "Google"
    GITHUB = "Github"
    LOCAL = "Local"


class PaymentStatus(str, Enum):
    PENDING = "Pending"
    COMPLETED = "Completed"
    FAILED = "Failed"
    REFUNDED = "Refunded"


class SubscriptionStatus(str, Enum):
    ACTIVE = "Active"
    CANCELLED = "Cancelled"
    EXPIRED = "Expired"
    PENDING = "Pending"


class CommentType(str, Enum):
    SCRIPT = "Script"
    BLOGPOST = "BlogPost"


class Status(str, Enum):
    ACHIEVED = "Achieved"
    LOCKED = "Locked"


# Base Model
class BaseSQLModel(SQLModel):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)


# Models
class Achievement(BaseSQLModel, table=True):
    name: str = Field(index=True, nullable=False, unique=True, max_length=50)
    description: Optional[str] = Field(default=None, max_length=200)
    status: Status = Field(nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default=None)
    users: List["UserAchievement"] = Relationship(back_populates="achievement")


class Activity(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    action_type: str = Field(nullable=False, max_length=50)
    details: Optional[str] = Field(default=None, max_length=500)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user: "User" = Relationship(back_populates="activities")


class AdminAction(BaseSQLModel, table=True):
    admin_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, index=True)
    action_type: str = Field(nullable=False, max_length=50)
    details: Optional[str] = Field(default=None, max_length=500)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    admin: "User" = Relationship(back_populates="admin_actions")


class Badge(BaseSQLModel, table=True):
    name: str = Field(index=True, nullable=False, unique=True, max_length=50)
    description: Optional[str] = Field(default=None, max_length=200)
    badge_type: BadgeType = Field(nullable=False)
    users: List["UserBadge"] = Relationship(back_populates="badge")


class BlogPostView(BaseSQLModel, table=True):
    blog_post_id: uuid.UUID = Field(foreign_key="blogpost.id", nullable=False, index=True)
    user_id: Optional[uuid.UUID] = Field(foreign_key="user.id", nullable=True, index=True)
    viewed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    blog_post: "BlogPost" = Relationship(back_populates="views")
    user: Optional["User"] = Relationship(back_populates="blog_post_views")


class Challenge(BaseSQLModel, table=True):
    name: str = Field(nullable=False, max_length=100)
    description: str = Field(nullable=False, max_length=200)
    type: str = Field(nullable=False, max_length=50)  # e.g., "daily", "weekly"
    target: int = Field(nullable=False)
    reward: str = Field(nullable=False, max_length=100)  # e.g., "100 XP", "Reviewer badge"
    progress: int = Field(default=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default=None)
    daily_challenges: List["DailyChallenge"] = Relationship(back_populates="challenge")


class Comment(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    content: str = Field(nullable=False, max_length=1000)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    script_id: Optional[uuid.UUID] = Field(foreign_key="script.id", nullable=True)
    blog_post_id: Optional[uuid.UUID] = Field(foreign_key="blogpost.id", nullable=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user: "User" = Relationship(back_populates="comments")
    script: Optional["Script"] = Relationship(back_populates="comments")
    blog_post: Optional["BlogPost"] = Relationship(back_populates="comments")


class DailyChallenge(BaseSQLModel, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    challenge_id: uuid.UUID = Field(foreign_key="challenge.id", nullable=False)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user: "User" = Relationship(back_populates="daily_challenges")
    challenge: "Challenge" = Relationship(back_populates="daily_challenges")


class Flag(BaseSQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    reason: str = Field(nullable=False, max_length=255)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    blog_post_id: Optional[uuid.UUID] = Field(foreign_key="blogpost.id", nullable=True)
    script_id: Optional[uuid.UUID] = Field(foreign_key="script.id", nullable=True)
    flagger_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    blog_post: Optional["BlogPost"] = Relationship(back_populates="flags")
    script: Optional["Script"] = Relationship(back_populates="flags")
    flagger: "User" = Relationship(back_populates="flags")


class Follow(BaseSQLModel, table=True):
    follower_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    followed_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    follower: "User" = Relationship(back_populates="following",
                                    sa_relationship_kwargs={"foreign_keys": "[Follow.follower_id]"})
    followed: "User" = Relationship(back_populates="followers",
                                    sa_relationship_kwargs={"foreign_keys": "[Follow.followed_id]"})
    __table_args__ = (
        Index(
            "unique_follow",
            "follower_id",
            "followed_id",
            unique=True,
        ),
    )


class GamificationEvent(BaseSQLModel, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    event_type: str = Field(nullable=False, max_length=50)
    xp_reward: int = Field(nullable=False)
    event_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user: "User" = Relationship(back_populates="gamification_events")


class GitHubRepo(BaseSQLModel, table=True):
    name: str = Field(index=True, nullable=False, max_length=100)
    url: str = Field(nullable=False, max_length=200)
    owner_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, index=True)
    owner: "User" = Relationship(back_populates="github_repos")


class HelpAnswer(BaseSQLModel, table=True):
    question_id: uuid.UUID = Field(foreign_key="helpquestion.id", nullable=False)
    responder_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, index=True)
    content: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    question: "HelpQuestion" = Relationship(back_populates="answers")
    responder: "User" = Relationship(back_populates="help_answers")


class HelpQuestion(BaseSQLModel, table=True):
    title: str = Field(nullable=False, max_length=100, index=True)
    content: str = Field(nullable=False)
    asker_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved: bool = Field(default=False)
    resolved_at: Optional[datetime] = Field(default=None)
    asker: "User" = Relationship(back_populates="help_questions")
    answers: List["HelpAnswer"] = Relationship(back_populates="question")


class Leaderboard(BaseSQLModel, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    ranking_criteria: str = Field(nullable=False, max_length=50, index=True)
    rank: int = Field(nullable=False)
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user: "User" = Relationship(back_populates="leaderboards")


class Like(BaseSQLModel, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, index=True)
    script_id: Optional[uuid.UUID] = Field(foreign_key="script.id", nullable=True, index=True)
    blog_post_id: Optional[uuid.UUID] = Field(foreign_key="blogpost.id", nullable=True, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user: "User" = Relationship(back_populates="likes")
    script: Optional["Script"] = Relationship(back_populates="likes")
    blog_post: Optional["BlogPost"] = Relationship(back_populates="likes")
    __table_args__ = (
        Index(
            "idx_like_content",
            "script_id",
            "blog_post_id",
        ),
    )


class Message(BaseSQLModel, table=True):
    sender_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    receiver_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, index=True)
    content: str = Field(nullable=False, max_length=1000)
    sent_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    sender: "User" = Relationship(back_populates="messages_sent",
                                  sa_relationship_kwargs={"foreign_keys": "[Message.sender_id]"})
    receiver: "User" = Relationship(back_populates="messages_received",
                                    sa_relationship_kwargs={"foreign_keys": "[Message.receiver_id]"})


class Notification(BaseSQLModel, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    message: str = Field(nullable=False, max_length=500)
    read: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user: "User" = Relationship(back_populates="notifications")


class PageView(BaseSQLModel, table=True):
    user_id: Optional[uuid.UUID] = Field(foreign_key="user.id", nullable=True, index=True)
    page_url: str = Field(nullable=False, max_length=200)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user: Optional["User"] = Relationship(back_populates="page_views")


class Payment(BaseSQLModel, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    amount: float = Field(nullable=False)
    currency: str = Field(nullable=False, max_length=10)
    status: PaymentStatus = Field(nullable=False)
    payment_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payment_reference: Optional[str] = Field(default=None, max_length=100)
    user: "User" = Relationship(back_populates="payments")


class ScriptView(BaseSQLModel, table=True):
    script_id: uuid.UUID = Field(foreign_key="script.id", nullable=False, index=True)
    user_id: Optional[uuid.UUID] = Field(foreign_key="user.id", nullable=True, index=True)
    viewed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    script: "Script" = Relationship(back_populates="views")
    user: Optional["User"] = Relationship(back_populates="script_views")


class SiteMetric(BaseSQLModel, table=True):
    metric_name: str = Field(nullable=False, max_length=100)
    value: float = Field(nullable=False)
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Subscription(BaseSQLModel, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    plan_id: uuid.UUID = Field(foreign_key="subscriptionplan.id", nullable=False)
    status: SubscriptionStatus = Field(nullable=False)
    start_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    end_date: Optional[datetime] = Field(default=None)
    cancel_date: Optional[datetime] = Field(default=None)
    user: "User" = Relationship(back_populates="subscriptions")
    plan: "SubscriptionPlan" = Relationship(back_populates="subscriptions")


class SubscriptionPlan(BaseSQLModel, table=True):
    name: str = Field(nullable=False, unique=True, max_length=50)
    price: float = Field(nullable=False)
    currency: str = Field(nullable=False, max_length=10)
    features: Optional[str] = Field(default=None, max_length=500)
    stripe_price_id: str = Field(nullable=False, max_length=100)
    subscriptions: List["Subscription"] = Relationship(back_populates="plan")


class Transaction(BaseSQLModel, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    amount: float = Field(nullable=False)
    transaction_type: str = Field(nullable=False, max_length=50)
    transaction_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    stripe_transaction_id: str = Field(nullable=False, max_length=100)
    user: "User" = Relationship(back_populates="transactions")


class Trophy(BaseSQLModel, table=True):
    name: str = Field(nullable=False, max_length=100)
    description: str = Field(nullable=False, max_length=200)
    trophy_level: TrophyLevel = Field(nullable=False)
    status: Status = Field(nullable=False)
    awarded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default=None)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    user: "User" = Relationship(back_populates="trophies")


class User(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True, index=True, unique=True)
    username: str = Field(index=True, unique=True, nullable=False, max_length=50)
    email: str = Field(index=True, unique=True, nullable=False, max_length=100)
    hashed_password: str = Field(nullable=False)
    auth_provider: AuthProvider = Field(default=AuthProvider.LOCAL)
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    followers_count: int = Field(default=0)
    following_count: int = Field(default=0)
    role: Role = Field(default=Role.USER)
    scripts_count: int = Field(default=0)
    blog_posts_count: int = Field(default=0)
    comments_count: int = Field(default=0)
    likes_count: int = Field(default=0)
    notifications_count: int = Field(default=0)
    messages_sent_count: int = Field(default=0)
    messages_received_count: int = Field(default=0)
    trophies_count: int = Field(default=0)
    user_achievements_count: int = Field(default=0)
    user_badges_count: int = Field(default=0)
    subscriptions_count: int = Field(default=0)
    transactions_count: int = Field(default=0)
    page_views_count: int = Field(default=0)
    gamification_events_count: int = Field(default=0)
    help_questions_count: int = Field(default=0)
    help_answers_count: int = Field(default=0)
    github_repos_count: int = Field(default=0)
    daily_challenges_count: int = Field(default=0)
    admin_actions_count: int = Field(default=0)
    activities_count: int = Field(default=0)
    flags_count: int = Field(default=0)
    script_views_count: int = Field(default=0)
    blog_post_views_count: int = Field(default=0)

    # Relationships
    activities: List["Activity"] = Relationship(back_populates="user")
    admin_actions: List["AdminAction"] = Relationship(back_populates="admin")
    blog_posts: List["BlogPost"] = Relationship(back_populates="author")
    blog_post_views: List["BlogPostView"] = Relationship(back_populates="user")
    comments: List["Comment"] = Relationship(back_populates="user")
    daily_challenges: List["DailyChallenge"] = Relationship(back_populates="user")
    flags: List["Flag"] = Relationship(back_populates="flagger")
    followers: List["Follow"] = Relationship(back_populates="followed",
                                             sa_relationship_kwargs={"foreign_keys": "[Follow.followed_id]"})
    following: List["Follow"] = Relationship(back_populates="follower",
                                             sa_relationship_kwargs={"foreign_keys": "[Follow.follower_id]"})
    gamification_events: List["GamificationEvent"] = Relationship(back_populates="user")
    github_repos: List["GitHubRepo"] = Relationship(back_populates="owner")
    help_answers: List["HelpAnswer"] = Relationship(back_populates="responder")
    help_questions: List["HelpQuestion"] = Relationship(back_populates="asker")
    leaderboards: List["Leaderboard"] = Relationship(back_populates="user")
    likes: List["Like"] = Relationship(back_populates="user")
    messages_received: List["Message"] = Relationship(back_populates="receiver",
                                                      sa_relationship_kwargs={"foreign_keys": "[Message.receiver_id]"})
    messages_sent: List["Message"] = Relationship(back_populates="sender",
                                                  sa_relationship_kwargs={"foreign_keys": "[Message.sender_id]"})
    notifications: List["Notification"] = Relationship(back_populates="user")
    page_views: List["PageView"] = Relationship(back_populates="user")
    payments: List["Payment"] = Relationship(back_populates="user")
    profile: "UserProfile" = Relationship(back_populates="user")
    scripts: List["Script"] = Relationship(back_populates="author")
    script_views: List["ScriptView"] = Relationship(back_populates="user")
    subscriptions: List["Subscription"] = Relationship(back_populates="user")
    transactions: List["Transaction"] = Relationship(back_populates="user")
    trophies: List["Trophy"] = Relationship(back_populates="user")
    user_achievements: List["UserAchievement"] = Relationship(back_populates="user")
    user_badges: List["UserBadge"] = Relationship(back_populates="user")
    user_settings: List["UserSettings"] = Relationship(back_populates="user")
    sent_messages: List["DirectMessage"] = Relationship(back_populates="sender", sa_relationship_kwargs={
        "foreign_keys": "[DirectMessage.sender_id]"})
    received_messages: List["DirectMessage"] = Relationship(back_populates="receiver", sa_relationship_kwargs={
        "foreign_keys": "[DirectMessage.receiver_id]"})
    owned_projects: List["Project"] = Relationship(back_populates="owner")
    projects: List["ProjectMember"] = Relationship(back_populates="user")
    project_roles: List["ProjectRoleAssignment"] = Relationship(back_populates="user")


class UserAchievement(BaseSQLModel, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, index=True)
    achievement_id: uuid.UUID = Field(foreign_key="achievement.id", nullable=False, index=True)
    achieved_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user: "User" = Relationship(back_populates="user_achievements")
    achievement: "Achievement" = Relationship(back_populates="users")


class UserBadge(BaseSQLModel, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, index=True)
    badge_id: uuid.UUID = Field(foreign_key="badge.id", nullable=False, index=True)
    awarded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user: "User" = Relationship(back_populates="user_badges")
    badge: "Badge" = Relationship(back_populates="users")


class UserProfile(BaseSQLModel, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, unique=True)
    bio: Optional[str] = Field(default=None, max_length=500)
    avatar_url: Optional[str] = Field(default=None, max_length=500)
    location: Optional[str] = Field(default=None, max_length=100)
    website: Optional[str] = Field(default=None, max_length=200)
    github_username: Optional[str] = Field(default=None, max_length=50)
    twitter_username: Optional[str] = Field(default=None, max_length=50)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user: "User" = Relationship(back_populates="profile")
    __table_args__ = (
        Index(
            "unique_user_profile",
            "user_id",
            unique=True,
        ),
    )


class UserSettings(BaseSQLModel, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, index=True)
    setting_name: str = Field(nullable=False, max_length=50)
    setting_value: str = Field(nullable=False, max_length=50)
    user: "User" = Relationship(back_populates="user_settings")


class BlogPost(BaseSQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(index=True, nullable=False, max_length=100)
    content: str = Field(nullable=False)
    author_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, index=True)
    image_url: Optional[str] = Field(default=None, max_length=200)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    author: "User" = Relationship(back_populates="blog_posts")
    likes: List["Like"] = Relationship(back_populates="blog_post")
    comments: List["Comment"] = Relationship(back_populates="blog_post")
    views: List["BlogPostView"] = Relationship(back_populates="blog_post")
    flags: List["Flag"] = Relationship(back_populates="blog_post")
    tags: list[str] = Field(sa_column=Column(JSON))
    category: Optional[str] = Field(default=None, max_length=50)


class Script(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(index=True, nullable=False, max_length=100)
    content: str = Field(nullable=False)
    description: Optional[str] = Field(default=None, max_length=200)
    instructions: Optional[str] = Field(default=None, max_length=200)
    language: str = Field(nullable=False, max_length=50)
    use_cases: str = Field(default=None, max_length=200)
    author_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    author: "User" = Relationship(back_populates="scripts")
    likes: List["Like"] = Relationship(back_populates="script")
    comments: List["Comment"] = Relationship(back_populates="script")
    flags: List["Flag"] = Relationship(back_populates="script")
    views: List["ScriptView"] = Relationship(back_populates="script")
    tags: list[str] = Field(sa_column=Column(JSON))
    grade: Optional[str] = Field(default=None, max_length=50)
    framework: Optional[str] = Field(default=None, max_length=50)
    license: Optional[str] = Field(default=None, max_length=50)
    category: Optional[str] = Field(default=None, max_length=50)



class DirectMessage(BaseSQLModel, table=True):
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default=None)
    sender_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    receiver_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, index=True)
    content: str = Field(nullable=False, max_length=1000)
    sent_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    sender: "User" = Relationship(back_populates="sent_messages",
                                  sa_relationship_kwargs={"foreign_keys": "[DirectMessage.sender_id]"})
    receiver: "User" = Relationship(back_populates="received_messages",
                                    sa_relationship_kwargs={"foreign_keys": "[DirectMessage.receiver_id]"})
    __table_args__ = (
        Index(
            "idx_direct_message",
            "sender_id",
            "receiver_id",
        ),
    )


class ProjectMember(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default=None, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="project.id")
    user_id: uuid.UUID = Field(foreign_key="user.id")

    project: "Project" = Relationship(back_populates="members")
    user: "User" = Relationship(back_populates="projects")


class Project(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(nullable=False, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    owner: "User" = Relationship(back_populates="owned_projects")
    members: List["ProjectMember"] = Relationship(back_populates="project")
    scripts: List["ProjectScript"] = Relationship(back_populates="project")
    roles: List["ProjectRole"] = Relationship(back_populates="project")
    assignments: List["ProjectRoleAssignment"] = Relationship(back_populates="project")


class ProjectScript(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    script_id: uuid.UUID = Field(foreign_key="script.id", nullable=False)
    project_id: uuid.UUID = Field(foreign_key="project.id", nullable=False)
    project: "Project" = Relationship(back_populates="scripts")
    script: "Script" = Relationship()


class ProjectRole(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(nullable=False, max_length=50)
    description: Optional[str] = Field(default=None, max_length=200)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default=None)
    project_id: uuid.UUID = Field(foreign_key="project.id", nullable=False)
    project: "Project" = Relationship(back_populates="roles")
    permissions: List["ProjectRolePermission"] = Relationship(back_populates="role")


class ProjectRolePermission(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    permission_name: str = Field(nullable=False, max_length=50)
    description: Optional[str] = Field(default=None, max_length=200)
    role_id: uuid.UUID = Field(foreign_key="projectrole.id", nullable=False)
    role: "ProjectRole" = Relationship(back_populates="permissions")


class ProjectRoleAssignment(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    role_id: uuid.UUID = Field(foreign_key="projectrole.id", nullable=False)
    project_id: uuid.UUID = Field(foreign_key="project.id", nullable=False)
    user: "User" = Relationship(back_populates="project_roles")
    role: "ProjectRole" = Relationship(back_populates="assignments")
    project: "Project" = Relationship(back_populates="assignments")


class ProjectRoleAssignmentPermission(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    role_assignment_id: uuid.UUID = Field(foreign_key="projectroleassignment.id", nullable=False)
    permission_name: str = Field(nullable=False, max_length=50)
    role_assignment: "ProjectRoleAssignment" = Relationship(back_populates="permissions")
