from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from uuid import UUID
from ...db.database import get_db
from ...db.schemas import (
    AchievementCreate, BadgeCreate, TrophyCreate, UserAchievementCreate, UserBadgeCreate,
    GamificationEventCreate, LeaderboardCreate, DailyChallengeCreate, ChallengeCreate
)
from ...services.gamification_service import GamificationService
from ...db.models import Achievement, Badge, Trophy, UserAchievement, UserBadge, GamificationEvent, Leaderboard, \
    DailyChallenge, Challenge
import logging

logger = logging.getLogger(__name__)

gamification_router = APIRouter()

def get_service(db: Session = Depends(get_db)) -> GamificationService:
    return GamificationService(db)

@gamification_router.post("/achievements/", response_model=Achievement, tags=["Achievements 🏆"], summary="Create an achievement", description="Create an achievement for a user")
def create_achievement(achievement_in: AchievementCreate, service: GamificationService = Depends(get_service)):
    try:
        return service.award_trophy(achievement_in.user_id, achievement_in.name)
    except Exception as e:
        logger.error(f"Error creating achievement: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@gamification_router.post("/badges/", response_model=Badge, tags=["Badges 🥇"])
def create_badge(badge_in: BadgeCreate, service: GamificationService = Depends(get_service)):
    try:
        return service.award_trophy(badge_in.user_id, badge_in.name)
    except Exception as e:
        logger.error(f"Error creating badge: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@gamification_router.post("/trophies/", response_model=Trophy, tags=["Trophies 🏅"])
def create_trophy(trophy_in: TrophyCreate, service: GamificationService = Depends(get_service)):
    try:
        return service.award_trophy(trophy_in.user_id, trophy_in.name)
    except Exception as e:
        logger.error(f"Error creating trophy: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@gamification_router.post("/user-achievements/", response_model=UserAchievement, tags=["User Achievements 🏆"])
def create_user_achievement(user_achievement_in: UserAchievementCreate, service: GamificationService = Depends(get_service)):
    try:
        return service.award_user_achievement(user_achievement_in.user_id, user_achievement_in.achievement_id)
    except Exception as e:
        logger.error(f"Error creating user achievement: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@gamification_router.post("/user-badges/", response_model=UserBadge, tags=["User Badges 🥇"])
def create_user_badge(user_badge_in: UserBadgeCreate, service: GamificationService = Depends(get_service)):
    try:
        return service.award_user_badge(user_badge_in.user_id, user_badge_in.badge_id)
    except Exception as e:
        logger.error(f"Error creating user badge: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@gamification_router.post("/gamification-events/", response_model=GamificationEvent, tags=["Gamification Events 🎮"])
def create_gamification_event(gamification_event_in: GamificationEventCreate, service: GamificationService = Depends(get_service)):
    try:
        return service.award_trophy(gamification_event_in.user_id, gamification_event_in.event_type)
    except Exception as e:
        logger.error(f"Error creating gamification event: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@gamification_router.post("/leaderboards/", response_model=Leaderboard, tags=["Leaderboards 📊"])
def create_leaderboard(leaderboard_in: LeaderboardCreate, service: GamificationService = Depends(get_service)):
    try:
        return service.award_trophy(leaderboard_in.user_id, leaderboard_in.ranking_criteria)
    except Exception as e:
        logger.error(f"Error creating leaderboard: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@gamification_router.post("/daily-challenges/", response_model=DailyChallenge, tags=["Daily Challenges 📅"])
def create_daily_challenge(daily_challenge_in: DailyChallengeCreate, service: GamificationService = Depends(get_service)):
    try:
        return service.award_trophy(daily_challenge_in.user_id, daily_challenge_in.description)
    except Exception as e:
        logger.error(f"Error creating daily challenge: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@gamification_router.post("/challenges/", response_model=Challenge, tags=["Challenges 🏁"])
def create_challenge(challenge_in: ChallengeCreate, service: GamificationService = Depends(get_service)):
    try:
        return service.award_trophy(challenge_in.user_id, challenge_in.description)
    except Exception as e:
        logger.error(f"Error creating challenge: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@gamification_router.get("/achievements/{achievement_id}", response_model=Achievement, tags=["Achievements 🏆"])
def get_achievement(achievement_id: UUID, service: GamificationService = Depends(get_service)):
    achievement = service.get_achievement(achievement_id)
    if not achievement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Achievement not found")
    return achievement

@gamification_router.put("/achievements/{achievement_id}", response_model=Achievement, tags=["Achievements 🏆"])
def update_achievement(achievement_id: UUID, achievement_in: AchievementCreate, service: GamificationService = Depends(get_service)):
    achievement = service.update_achievement(achievement_id, achievement_in)
    if not achievement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Achievement not found")
    return achievement

@gamification_router.delete("/achievements/{achievement_id}", tags=["Achievements 🏆"])
def delete_achievement(achievement_id: UUID, service: GamificationService = Depends(get_service)):
    service.delete_achievement(achievement_id)
    return {"message": "Achievement deleted successfully"}

@gamification_router.get("/badges/{badge_id}", response_model=Badge, tags=["Badges 🥇"])
def get_badge(badge_id: UUID, service: GamificationService = Depends(get_service)):
    badge = service.get_badge(badge_id)
    if not badge:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Badge not found")
    return badge

@gamification_router.put("/badges/{badge_id}", response_model=Badge, tags=["Badges 🥇"])
def update_badge(badge_id: UUID, badge_in: BadgeCreate, service: GamificationService = Depends(get_service)):
    badge = service.update_badge(badge_id, badge_in)
    if not badge:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Badge not found")
    return badge

@gamification_router.delete("/badges/{badge_id}", tags=["Badges 🥇"])
def delete_badge(badge_id: UUID, service: GamificationService = Depends(get_service)):
    service.delete_badge(badge_id)
    return {"message": "Badge deleted successfully"}

@gamification_router.get("/trophies/{trophy_id}", response_model=Trophy, tags=["Trophies 🏅"])
def get_trophy(trophy_id: UUID, service: GamificationService = Depends(get_service)):
    trophy = service.get_trophy(trophy_id)
    if not trophy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trophy not found")
    return trophy

@gamification_router.put("/trophies/{trophy_id}", response_model=Trophy, tags=["Trophies 🏅"])
def update_trophy(trophy_id: UUID, trophy_in: TrophyCreate, service: GamificationService = Depends(get_service)):
    trophy = service.update_trophy(trophy_id, trophy_in)
    if not trophy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trophy not found")
    return trophy

@gamification_router.delete("/trophies/{trophy_id}", tags=["Trophies 🏅"])
def delete_trophy(trophy_id: UUID, service: GamificationService = Depends(get_service)):
    service.delete_trophy(trophy_id)
    return {"message": "Trophy deleted successfully"}

@gamification_router.get("/user-achievements/{user_achievement_id}", response_model=UserAchievement, tags=["User Achievements 🏆"])
def get_user_achievement(user_achievement_id: UUID, service: GamificationService = Depends(get_service)):
    user_achievement = service.get_user_achievement(user_achievement_id)
    if not user_achievement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Achievement not found")
    return user_achievement

@gamification_router.put("/user-achievements/{user_achievement_id}", response_model=UserAchievement, tags=["User Achievements 🏆"])
def update_user_achievement(user_achievement_id: UUID, user_achievement_in: UserAchievementCreate, service: GamificationService = Depends(get_service)):
    user_achievement = service.update_user_achievement(user_achievement_id, user_achievement_in)
    if not user_achievement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Achievement not found")
    return user_achievement

@gamification_router.delete("/user-achievements/{user_achievement_id}", tags=["User Achievements 🏆"])
def delete_user_achievement(user_achievement_id: UUID, service: GamificationService = Depends(get_service)):
    service.delete_user_achievement(user_achievement_id)
    return {"message": "User Achievement deleted successfully"}

@gamification_router.get("/user-badges/{user_badge_id}", response_model=UserBadge, tags=["User Badges 🥇"])
def get_user_badge(user_badge_id: UUID, service: GamificationService = Depends(get_service)):
    user_badge = service.get_user_badge(user_badge_id)
    if not user_badge:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Badge not found")
    return user_badge

@gamification_router.put("/user-badges/{user_badge_id}", response_model=UserBadge, tags=["User Badges 🥇"])
def update_user_badge(user_badge_id: UUID, user_badge_in: UserBadgeCreate, service: GamificationService = Depends(get_service)):
    user_badge = service.update_user_badge(user_badge_id, user_badge_in)
    if not user_badge:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Badge not found")
    return user_badge

@gamification_router.delete("/user-badges/{user_badge_id}", tags=["User Badges 🥇"])
def delete_user_badge(user_badge_id: UUID, service: GamificationService = Depends(get_service)):
    service.delete_user_badge(user_badge_id)
    return {"message": "User Badge deleted successfully"}

@gamification_router.get("/gamification-events/{gamification_event_id}", response_model=GamificationEvent, tags=["Gamification Events 🎮"])
def get_gamification_event(gamification_event_id: UUID, service: GamificationService = Depends(get_service)):
    gamification_event = service.get_gamification_event(gamification_event_id)
    if not gamification_event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gamification Event not found")
    return gamification_event

@gamification_router.put("/gamification-events/{gamification_event_id}", response_model=GamificationEvent, tags=["Gamification Events 🎮"])
def update_gamification_event(gamification_event_id: UUID, gamification_event_in: GamificationEventCreate, service: GamificationService = Depends(get_service)):
    gamification_event = service.update_gamification_event(gamification_event_id, gamification_event_in)
    if not gamification_event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gamification Event not found")
    return gamification_event

@gamification_router.delete("/gamification-events/{gamification_event_id}", tags=["Gamification Events 🎮"])
def delete_gamification_event(gamification_event_id: UUID, service: GamificationService = Depends(get_service)):
    service.delete_gamification_event(gamification_event_id)
    return {"message": "Gamification Event deleted successfully"}

@gamification_router.get("/leaderboards/{leaderboard_id}", response_model=Leaderboard, tags=["Leaderboards 📊"])
def get_leaderboard(leaderboard_id: UUID, service: GamificationService = Depends(get_service)):
    leaderboard = service.get_leaderboard(leaderboard_id)
    if not leaderboard:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leaderboard not found")
    return leaderboard

@gamification_router.put("/leaderboards/{leaderboard_id}", response_model=Leaderboard, tags=["Leaderboards 📊"])
def update_leaderboard(leaderboard_id: UUID, leaderboard_in: LeaderboardCreate, service: GamificationService = Depends(get_service)):
    leaderboard = service.update_leaderboard(leaderboard_id, leaderboard_in)
    if not leaderboard:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leaderboard not found")
    return leaderboard

@gamification_router.delete("/leaderboards/{leaderboard_id}", tags=["Leaderboards 📊"])
def delete_leaderboard(leaderboard_id: UUID, service: GamificationService = Depends(get_service)):
    service.delete_leaderboard(leaderboard_id)
    return {"message": "Leaderboard deleted successfully"}

@gamification_router.get("/daily-challenges/{daily_challenge_id}", response_model=DailyChallenge, tags=["Daily Challenges 📅"])
def get_daily_challenge(daily_challenge_id: UUID, service: GamificationService = Depends(get_service)):
    daily_challenge = service.get_daily_challenge(daily_challenge_id)
    if not daily_challenge:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Daily Challenge not found")
    return daily_challenge

@gamification_router.put("/daily-challenges/{daily_challenge_id}", response_model=DailyChallenge, tags=["Daily Challenges 📅"])
def update_daily_challenge(daily_challenge_id: UUID, daily_challenge_in: DailyChallengeCreate, service: GamificationService = Depends(get_service)):
    daily_challenge = service.update_daily_challenge(daily_challenge_id, daily_challenge_in)
    if not daily_challenge:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Daily Challenge not found")
    return daily_challenge

@gamification_router.delete("/daily-challenges/{daily_challenge_id}", tags=["Daily Challenges 📅"])
def delete_daily_challenge(daily_challenge_id: UUID, service: GamificationService = Depends(get_service)):
    service.delete_daily_challenge(daily_challenge_id)
    return {"message": "Daily Challenge deleted successfully"}

@gamification_router.get("/challenges/{challenge_id}", response_model=Challenge, tags=["Challenges 🏁"])
def get_challenge(challenge_id: UUID, service: GamificationService = Depends(get_service)):
    challenge = service.get_challenge(challenge_id)
    if not challenge:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Challenge not found")
    return challenge

@gamification_router.put("/challenges/{challenge_id}", response_model=Challenge, tags=["Challenges 🏁"])
def update_challenge(challenge_id: UUID, challenge_in: ChallengeCreate, service: GamificationService = Depends(get_service)):
    challenge = service.update_challenge(challenge_id, challenge_in)
    if not challenge:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Challenge not found")
    return challenge

@gamification_router.delete("/challenges/{challenge_id}", tags=["Challenges 🏁"])
def delete_challenge(challenge_id: UUID, service: GamificationService = Depends(get_service)):
    service.delete_challenge(challenge_id)
    return {"message": "Challenge deleted successfully"}