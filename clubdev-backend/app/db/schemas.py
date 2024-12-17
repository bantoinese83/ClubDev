from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, HttpUrl, constr, Field
import uuid


# Base Schemas
class BaseResponse(BaseModel):
    message: str
    success: bool


class PaginatedResponse(BaseModel):
    items: List[dict]
    total: int
    page: int
    size: int
    pages: int


# User Schemas
class UserBase(BaseModel):
    username: constr(min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    password: constr(min_length=8)


class UserUpdate(BaseModel):
    username: Optional[constr(min_length=3, max_length=50)] = None
    email: Optional[EmailStr] = None
    password: Optional[constr(min_length=8)] = None


class UserRead(UserBase):
    id: uuid.UUID
    is_active: bool
    is_superuser: bool
    created_at: datetime
    auth_provider: str

    class Config:
        from_attributes = True


# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: Optional[str] = None


class TokenData(BaseModel):
    username: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


# Profile Schemas
class UserProfileBase(BaseModel):
    bio: Optional[str] = None
    avatar_url: Optional[HttpUrl] = None
    location: Optional[str] = None
    website: Optional[HttpUrl] = None
    github_username: Optional[str] = None
    twitter_username: Optional[str] = None


class UserProfileCreate(UserProfileBase):
    pass


class UserProfileUpdate(UserProfileBase):
    pass


class UserProfileRead(UserProfileBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ScriptBase(BaseModel):
    title: constr(min_length=1, max_length=100)
    content: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    instructions: Optional[str] = None
    category: str
    language: str
    use_cases: Optional[str] = None
    framework: Optional[str] = None
    license: Optional[str] = None
    grade: Optional[str] = None


class ScriptCreate(ScriptBase):
    author_id: uuid.UUID
    title: str
    content: str
    category: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    instructions: Optional[str] = None
    use_cases: Optional[str] = None
    framework: Optional[str] = None
    license: Optional[str] = None
    grade: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ScriptUpdate(ScriptBase):
    title: Optional[constr(min_length=1, max_length=100)] = None
    content: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    instructions: Optional[str] = None
    use_cases: Optional[str] = None
    framework: Optional[str] = None
    license: Optional[str] = None
    grade: Optional[str] = None


class ScriptRead(ScriptBase):
    id: uuid.UUID
    author_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    likes_count: Optional[int] = 0
    comments_count: Optional[int] = 0
    views_count: Optional[int] = 0

    class Config:
        from_attributes = True


# Blog Post Schemas
class BlogPostBase(BaseModel):
    title: constr(min_length=1, max_length=100)
    content: str
    tags: Optional[List[str]] = None
    category: Optional[str] = None


class BlogPostCreate(BlogPostBase):
    author_id: uuid.UUID
    title: str
    content: str
    tags: Optional[List[str]] = None
    category: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class BlogPostUpdate(BlogPostBase):
    title: Optional[constr(min_length=1, max_length=100)] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None


class BlogPostRead(BlogPostBase):
    id: uuid.UUID
    author_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    likes_count: Optional[int] = 0
    comments_count: Optional[int] = 0
    views_count: Optional[int] = 0

    class Config:
        from_attributes = True


# Comment Schemas
class CommentBase(BaseModel):
    content: constr(min_length=1, max_length=1000)


class CommentCreate(CommentBase):
    user_id: uuid.UUID
    script_id: Optional[uuid.UUID] = None
    blog_post_id: Optional[uuid.UUID] = None


class CommentUpdate(CommentBase):
    pass


class CommentRead(CommentBase):
    id: uuid.UUID
    user_id: uuid.UUID
    script_id: Optional[uuid.UUID]
    blog_post_id: Optional[uuid.UUID]
    created_at: datetime

    class Config:
        from_attributes = True


# Like Schemas
class LikeCreate(BaseModel):
    user_id: uuid.UUID
    script_id: Optional[uuid.UUID] = None
    blog_post_id: Optional[uuid.UUID] = None


class LikeRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    script_id: Optional[uuid.UUID]
    blog_post_id: Optional[uuid.UUID]
    created_at: datetime

    class Config:
        from_attributes = True


class LikeRequest(BaseModel):
    user_id: uuid.UUID
    content_id: uuid.UUID
    content_type: str


class CommentRequest(BaseModel):
    user_id: uuid.UUID
    content_id: uuid.UUID
    content_type: str
    comment_text: str


class FlagRequest(BaseModel):
    user_id: uuid.UUID
    content_id: uuid.UUID
    content_type: str
    reason: str


# Help Schemas
class HelpQuestionBase(BaseModel):
    content: str


class HelpQuestionCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    content: str
    asker_id: uuid.UUID


class HelpQuestionRead(HelpQuestionBase):
    id: uuid.UUID
    asker_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True


class HelpAnswerBase(BaseModel):
    content: str


class HelpAnswerCreate(BaseModel):
    question_id: uuid.UUID
    responder_id: uuid.UUID
    content: str


class HelpAnswerRead(HelpAnswerBase):
    id: uuid.UUID
    responder_id: uuid.UUID
    question_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True


# Notification Schemas
class NotificationBase(BaseModel):
    message: str


class NotificationCreate(NotificationBase):
    user_id: uuid.UUID


class NotificationRead(NotificationBase):
    id: uuid.UUID
    user_id: uuid.UUID
    read: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Message Schemas
class MessageBase(BaseModel):
    content: str


class MessageCreate(MessageBase):
    receiver_id: uuid.UUID


class MessageRead(MessageBase):
    id: uuid.UUID
    sender_id: uuid.UUID
    receiver_id: uuid.UUID
    sent_at: datetime

    class Config:
        from_attributes = True


# Subscription Schemas
class SubscriptionPlanBase(BaseModel):
    name: str
    price: float
    currency: str
    features: Optional[str] = None


class SubscriptionPlanCreate(SubscriptionPlanBase):
    pass


class SubscriptionPlanRead(SubscriptionPlanBase):
    id: uuid.UUID

    class Config:
        from_attributes = True


class SubscriptionBase(BaseModel):
    plan_id: uuid.UUID


class SubscriptionCreate(SubscriptionBase):
    pass


class SubscriptionRead(SubscriptionBase):
    id: uuid.UUID
    user_id: uuid.UUID
    status: str
    start_date: datetime
    end_date: Optional[datetime]
    cancel_date: Optional[datetime]

    class Config:
        from_attributes = True


# Achievement and Badge Schemas
class AchievementBase(BaseModel):
    name: str
    description: Optional[str] = None


class AchievementCreate(AchievementBase):
    pass


class AchievementRead(AchievementBase):
    id: uuid.UUID

    class Config:
        from_attributes = True


class BadgeBase(BaseModel):
    name: str
    description: Optional[str] = None
    badge_type: str


class BadgeCreate(BadgeBase):
    pass


class BadgeRead(BadgeBase):
    id: uuid.UUID

    class Config:
        from_attributes = True


# Error Schemas
class HTTPError(BaseModel):
    detail: str


# Search Schemas
class SearchResult(BaseModel):
    type: str
    id: uuid.UUID
    title: str
    content: str
    created_at: datetime
    author_id: uuid.UUID


class SearchResponse(BaseModel):
    results: List[SearchResult]
    total: int


# Flag Schemas
class FlagCreate(BaseModel):
    user_id: uuid.UUID
    flagger_id: uuid.UUID
    script_id: Optional[uuid.UUID] = None
    blog_post_id: Optional[uuid.UUID] = None
    reason: str


# Trophy Schemas
class TrophyCreate(BaseModel):
    user_id: uuid.UUID
    trophy_level: str
    description: str


# User Achievement Schemas
class UserAchievementBase(BaseModel):
    user_id: uuid.UUID
    achievement_id: uuid.UUID


class UserAchievementCreate(UserAchievementBase):
    pass


# User Badge Schemas
class UserBadgeBase(BaseModel):
    user_id: uuid.UUID
    badge_id: uuid.UUID


class UserBadgeCreate(UserBadgeBase):
    pass


# Gamification Event Schemas
class GamificationEventBase(BaseModel):
    user_id: uuid.UUID
    event_type: str
    xp_reward: int


class GamificationEventCreate(GamificationEventBase):
    description: str


# Leaderboard Schemas
class LeaderboardBase(BaseModel):
    user_id: uuid.UUID
    ranking_criteria: str
    rank: int


class LeaderboardCreate(LeaderboardBase):
    description: str


# Daily Challenge Schemas
class DailyChallengeBase(BaseModel):
    user_id: uuid.UUID
    challenge_id: str
    completed: bool = False


class DailyChallengeCreate(DailyChallengeBase):
    description: str
    reward_xp: int


# Challenge Schemas
class ChallengeBase(BaseModel):
    description: str
    reward_xp: int


class ChallengeCreate(ChallengeBase):
    title: str


# Follow Schemas
class FollowBase(BaseModel):
    follower_id: uuid.UUID
    followed_id: uuid.UUID


class FollowCreate(FollowBase):
    created_at: datetime


# Activity Schemas
class ActivityBase(BaseModel):
    user_id: uuid.UUID
    action_type: str
    details: Optional[str] = None


class ActivityCreate(ActivityBase):
    created_at: datetime


# Admin Action Schemas
class AdminActionBase(BaseModel):
    admin_id: uuid.UUID
    action_type: str
    details: Optional[str] = None


class AdminActionCreate(AdminActionBase):
    pass


class AdminActionUpdate(AdminActionBase):
    pass


# GitHub Repo Schemas
class GitHubRepoBase(BaseModel):
    name: str
    url: str
    owner_id: uuid.UUID


class GitHubRepoCreate(GitHubRepoBase):
    pass


class GitHubRepoUpdate(GitHubRepoBase):
    name: Optional[str] = None
    url: Optional[str] = None
    owner_id: Optional[uuid.UUID] = None


class DirectMessageBase(BaseModel):
    content: str


class DirectMessageCreate(DirectMessageBase):
    receiver_id: uuid.UUID
    sender_id: uuid.UUID


class DirectMessageRead(DirectMessageBase):
    id: uuid.UUID
    sender_id: uuid.UUID
    receiver_id: uuid.UUID
    sent_at: datetime

    class Config:
        from_attributes = True


class HelpQuestionUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class HelpAnswerUpdate(BaseModel):
    content: Optional[str] = None


class GitHubRepoRead(GitHubRepoBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GitHubRepoDetail(GitHubRepoBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    owner: dict

    class Config:
        from_attributes = True


class GitHubRepoForkResponse(BaseModel):
    message: str
    success: bool
    forked_repo: dict


class AdminActionRead(AdminActionBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DirectMessageUpdate(BaseModel):
    content: Optional[str] = None
    receiver_id: Optional[uuid.UUID] = None
    sender_id: Optional[uuid.UUID] = None


# Project Schemas
class ProjectBase(BaseModel):
    name: constr(min_length=1, max_length=100)
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    owner_id: uuid.UUID



class ProjectUpdate(ProjectBase):
    name: Optional[constr(min_length=1, max_length=100)] = None
    description: Optional[str] = None


class ProjectRead(ProjectBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Project Member Schemas
class ProjectMemberBase(BaseModel):
    project_id: uuid.UUID
    user_id: uuid.UUID


class ProjectMemberCreate(ProjectMemberBase):
    pass


class ProjectMemberRead(ProjectMemberBase):
    id: uuid.UUID

    class Config:
        from_attributes = True

    # Project Role Schemas


class ProjectRoleBase(BaseModel):
    name: constr(min_length=1, max_length=50)
    description: Optional[str] = None


class ProjectRoleCreate(ProjectRoleBase):
    project_id: uuid.UUID


class ProjectRoleUpdate(ProjectRoleBase):
    name: Optional[constr(min_length=1, max_length=50)] = None
    description: Optional[str] = None


class ProjectRoleRead(ProjectRoleBase):
    id: uuid.UUID
    project_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

    # Project Role Permission Schemas


class ProjectRolePermissionBase(BaseModel):
    permission_name: constr(min_length=1, max_length=50)
    description: Optional[str] = None


class ProjectRolePermissionCreate(ProjectRolePermissionBase):
    role_id: uuid.UUID


class ProjectRolePermissionRead(ProjectRolePermissionBase):
    id: uuid.UUID
    role_id: uuid.UUID

    class Config:
        from_attributes = True

    # Project Role Assignment Schemas


class ProjectRoleAssignmentBase(BaseModel):
    user_id: uuid.UUID
    role_id: uuid.UUID
    project_id: uuid.UUID


class ProjectRoleAssignmentCreate(ProjectRoleAssignmentBase):
    pass


class ProjectRoleAssignmentRead(ProjectRoleAssignmentBase):
    id: uuid.UUID

    class Config:
        from_attributes = True

    # Project Role Assignment Permission Schemas


class ProjectRoleAssignmentPermissionBase(BaseModel):
    role_assignment_id: uuid.UUID
    permission_name: constr(min_length=1, max_length=50)


class ProjectRoleAssignmentPermissionCreate(ProjectRoleAssignmentPermissionBase):
    pass


class ProjectRoleAssignmentPermissionRead(ProjectRoleAssignmentPermissionBase):
    id: uuid.UUID

    class Config:
        from_attributes = True


class ProjectScriptCreate(BaseModel):
    title: constr(min_length=1, max_length=100)
    content: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    instructions: Optional[str] = None
    category: str