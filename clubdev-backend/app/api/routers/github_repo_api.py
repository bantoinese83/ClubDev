from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List
from ...db.database import get_db
from ...services.github_repo_service import GitHubRepoService
from ...db.schemas import GitHubRepoRead, GitHubRepoDetail, GitHubRepoForkResponse
from ...core.exceptions import DatabaseError, ItemNotFoundError
import logging

github_repo_router = APIRouter()
logger = logging.getLogger(__name__)


@github_repo_router.get("/github/repos", response_model=List[GitHubRepoRead], tags=["GitHub 📄🍴📂"])
async def get_all_repos(token: str, db: Session = Depends(get_db)):
    service = GitHubRepoService(db)
    try:
        repos = await service.get_all_repos_from_github(token)
        return repos
    except DatabaseError as e:
        logger.error(f"Database error fetching all repos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error fetching repositories")
    except Exception as e:
        logger.error(f"Error fetching all repos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error fetching repositories")

@github_repo_router.get("/github/repos/{owner}/{repo}", response_model=GitHubRepoDetail, tags=["GitHub 📄🍴📂"])
async def get_repo(owner: str, repo: str, token: str, db: Session = Depends(get_db)):
    service = GitHubRepoService(db)
    try:
        repo_detail = await service.get_repo_from_github(token, owner, repo)
        return repo_detail
    except ItemNotFoundError as e:
        logger.error(f"Repository not found: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found")
    except DatabaseError as e:
        logger.error(f"Database error fetching repo {owner}/{repo}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error fetching repository details")
    except Exception as e:
        logger.error(f"Error fetching repo {owner}/{repo}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error fetching repository details")

@github_repo_router.post("/github/repos/{owner}/{repo}/fork", response_model=GitHubRepoForkResponse, tags=["GitHub 📄🍴📂"])
async def fork_repo(owner: str, repo: str, token: str, db: Session = Depends(get_db)):
    service = GitHubRepoService(db)
    try:
        fork_response = await service.fork_repo_on_github(token, owner, repo)
        return fork_response
    except DatabaseError as e:
        logger.error(f"Database error forking repo {owner}/{repo}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error forking repository")
    except Exception as e:
        logger.error(f"Error forking repo {owner}/{repo}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error forking repository")