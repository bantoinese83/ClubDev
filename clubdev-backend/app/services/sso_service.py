import logging
from datetime import datetime, timezone

import httpx
from fastapi import HTTPException, status
from sqlmodel import Session, select

from ..core.security import create_access_token
from ..core.config import settings
from ..db.models import AuthProvider, User, UserProfile


class SSOLoginHandler:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    async def exchange_code_for_token(code: str) -> dict:
        data = {
            "code": code,
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "redirect_uri": settings.google_redirect_uri,
            "grant_type": "authorization_code",
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(settings.google_token_url, data=data)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to exchange code for token",
                )
            return response.json()

    @staticmethod
    async def get_user_info(access_token: str) -> dict:
        headers = {"Authorization": f"Bearer {access_token}"}
        async with httpx.AsyncClient() as client:
            response = await client.get(settings.google_userinfo_url, headers=headers)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to retrieve user info",
                )
            return response.json()

    async def handle_google_login(self, google_user_info: dict) -> dict:
        try:
            email = google_user_info.get("email")
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email not provided by Google",
                )

            statement = select(User).where(User.email == email)
            user = self.db.exec(statement).first()

            if not user:
                user = User(
                    email=email,
                    username=google_user_info.get("name", email.split("@")[0]),
                    auth_provider=AuthProvider.GOOGLE,
                    hashed_password="",
                    is_active=True,
                )
                self.db.add(user)
                self.db.commit()
                self.db.refresh(user)

            # Ensure user profile is created
            profile = self.db.exec(select(UserProfile).where(UserProfile.user_id == user.id)).first()
            if not profile:
                profile = UserProfile(
                    user_id=user.id,
                    avatar_url=google_user_info.get("picture"),
                    created_at=datetime.now(timezone.utc),
                )
                self.db.add(profile)
                self.db.commit()

            access_token = create_access_token(data={"sub": user.username})

            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": {"id": user.id, "email": user.email, "username": user.username},
            }

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error during Google login: {str(e)}",
            )

    @staticmethod
    async def exchange_github_code_for_token(code: str) -> dict:
        data = {
            "code": code,
            "client_id": settings.github_client_id,
            "client_secret": settings.github_client_secret,
            "redirect_uri": settings.github_redirect_uri,
        }
        headers = {"Accept": "application/json"}
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.github_token_url, data=data, headers=headers
            )

            logging.info(f"GitHub token response status: {response.status_code}")
            logging.info(f"GitHub token response content: {response.content}")
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to exchange code for token",
                )
            token_data = response.json()
            if "access_token" not in token_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Access token not found in the response",
                )
            return token_data

    @staticmethod
    async def get_github_user_info(access_token: str) -> dict:
        headers = {"Authorization": f"Bearer {access_token}"}
        async with httpx.AsyncClient() as client:
            response = await client.get(settings.github_userinfo_url, headers=headers)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to retrieve user info",
                )
            user_info = response.json()

            # Fetch email if not provided
            if "email" not in user_info or not user_info["email"]:
                email_response = await client.get(
                    "https://api.github.com/user/emails", headers=headers
                )
                if email_response.status_code == 200:
                    emails = email_response.json()
                    primary_email = next(
                        (
                            email["email"]
                            for email in emails
                            if email["primary"] and email["verified"]
                        ),
                        None,
                    )
                    if primary_email:
                        user_info["email"] = primary_email
                    else:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Email not provided by GitHub",
                        )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Failed to retrieve user email",
                    )
            return user_info

    async def handle_github_login(self, github_user_info: dict) -> dict:
        try:
            email = github_user_info.get("email")
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email not provided by GitHub",
                )

            statement = select(User).where(User.email == email)
            user = self.db.exec(statement).first()

            if not user:
                user = User(
                    email=email,
                    username=github_user_info.get("login", email.split("@")[0]),
                    auth_provider=AuthProvider.GITHUB,
                    hashed_password="",
                    is_active=True,
                )
                self.db.add(user)
                self.db.commit()
                self.db.refresh(user)

            # Ensure user profile is created
            profile = self.db.exec(select(UserProfile).where(UserProfile.user_id == user.id)).first()
            if not profile:
                profile = UserProfile(
                    user_id=user.id,
                    avatar_url=github_user_info.get("avatar_url"),
                    created_at=datetime.now(timezone.utc),
                )
                self.db.add(profile)
                self.db.commit()

            access_token = create_access_token(data={"sub": user.username})

            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": {"id": user.id, "email": user.email, "username": user.username},
            }

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error during GitHub login: {str(e)}",
            )
