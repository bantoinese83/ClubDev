from datetime import datetime, timezone

import httpx
from fastapi import HTTPException, status
from jose import ExpiredSignatureError
from jose.jwt import decode
from python_multipart.exceptions import DecodeError
from sqlmodel import Session
from ..core.config import settings


class GitHubRepoService:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    async def verify_token(token: str) -> bool:
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        async with httpx.AsyncClient() as client:
            response = await client.get("https://api.github.com/user", headers=headers)
            return response.status_code == 200

    @staticmethod
    def is_token_expired(token: str) -> bool:
        try:
            decoded_token = decode(token, options={"verify_signature": False}, key=settings.secret_key)
            expiration_time = datetime.fromtimestamp(decoded_token["exp"], timezone.utc)
            return datetime.now(timezone.utc) > expiration_time
        except (ExpiredSignatureError, DecodeError, KeyError):
            return True

    @staticmethod
    async def refresh_github_token(refresh_token: str) -> str:
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": settings.github_client_id,
            "client_secret": settings.github_client_secret
        }
        async with httpx.AsyncClient() as client:
            response = await client.post("https://github.com/login/oauth/access_token", data=data)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to refresh GitHub token"
                )
            return response.json().get("access_token")

    @staticmethod
    async def get_repo_from_github(token: str, owner: str, repo: str) -> dict:
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://api.github.com/repos/{owner}/{repo}", headers=headers)
            if response.status_code == 401:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired GitHub token"
                )
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to get repository from GitHub: {response.json()}"
                )
            return response.json()

    @staticmethod
    async def get_all_repos_from_github(token: str) -> dict:
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        async with httpx.AsyncClient() as client:
            response = await client.get("https://api.github.com/user/repos", headers=headers)
            if response.status_code == 401:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired GitHub token"
                )
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to get repositories from GitHub: {response.json()}"
                )
            return response.json()

    @staticmethod
    async def fork_repo_on_github(token: str, owner: str, repo: str) -> dict:
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(f"https://api.github.com/repos/{owner}/{repo}/forks", headers=headers)
            if response.status_code == 401:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired GitHub token"
                )
            if response.status_code != 202:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to fork repository on GitHub: {response.json()}"
                )
            return response.json()