import logging
from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.responses import RedirectResponse
from passlib.context import CryptContext
from sqlmodel import Session
from urllib.parse import urlencode

from ...core.security import create_access_token, authenticate_user, get_password_hash, verify_token, \
    create_refresh_token
from ...core.config import settings
from ...db.database import get_db
from ...db.schemas import UserCreate, UserRead, LoginRequest, Token
from ...services.sso_service import SSOLoginHandler
from ...services.user_service import UserService
from ...db.schemas import UserProfileCreate
from ...db.models import User, AuthProvider
from ...utils.s3_util import S3Util

logger = logging.getLogger(__name__)
auth_router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@auth_router.post(
    "/auth/signup",
    response_model=UserRead,
    tags=["Authentication 🔐"],
    description="Sign up a new user",
    operation_id="signup_user"
)
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    try:
        hashed_password = get_password_hash(user.password)
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
            auth_provider=AuthProvider.LOCAL,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        # Create user profile
        user_service = UserService(db, S3Util())
        user_profile = UserProfileCreate()
        user_service.create_user_profile(db_user.id, user_profile)

        logger.info(f"User {user.username} signed up successfully.")
        return db_user
    except Exception as e:
        logger.error(f"Error signing up user {user.username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error signing up user",
        )

@auth_router.post(
    "/auth/login",
    tags=["Authentication 🔐"],
    description="Log in a user and return access and refresh tokens",
    operation_id="login_user"
)
async def login(login_request: LoginRequest, db: Session = Depends(get_db)):
    try:
        user = authenticate_user(login_request.username, login_request.password, db)
        if not user:
            logger.warning(f"Invalid login attempt for username: {login_request.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check if user profile exists, if not create one
        user_service = UserService(db, S3Util())
        if not user_service.get_user_profile(user.id):
            user_profile = UserProfileCreate(bio="", avatar_url="", location="", website="")
            user_service.create_user_profile(user_id=user.id, user_profile=user_profile)

        access_token = create_access_token(data={"sub": user.username})
        refresh_token = create_refresh_token(data={"sub": user.username})
        logger.info(f"User {login_request.username} logged in successfully.")
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    except Exception as e:
        logger.error(f"Error logging in user {login_request.username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error logging in user",
        )

@auth_router.get(
    "/auth/google",
    tags=["Authentication 🔐"],
    description="Redirect to Google OAuth 2.0 authorization endpoint",
    operation_id="google_login"
)
async def google_login():
    try:
        params = {
            "client_id": settings.google_client_id,
            "redirect_uri": settings.google_redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "consent",
        }
        url = f"{settings.google_auth_url}?{urlencode(params)}"
        logger.info("Redirecting to Google OAuth 2.0 authorization endpoint.")
        return RedirectResponse(url)
    except Exception as e:
        logger.error(f"Error during Google login redirection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during Google login redirection",
        )

@auth_router.get(
    "/auth/google/callback",
    tags=["Authentication 🔐"],
    description="Handle Google OAuth 2.0 callback",
    operation_id="google_callback"
)
async def google_callback(code: str, db: Session = Depends(get_db)):
    try:
        sso_handler = SSOLoginHandler(db)
        token_data = await sso_handler.exchange_code_for_token(code)
        google_user_info = await sso_handler.get_user_info(token_data["access_token"])
        logger.info("Google OAuth 2.0 callback handled successfully.")
        return await sso_handler.handle_google_login(google_user_info)
    except Exception as e:
        logger.error(f"Error handling Google OAuth 2.0 callback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error handling Google OAuth 2.0 callback",
        )

@auth_router.get(
    "/auth/github",
    tags=["Authentication 🔐"],
    description="Redirect to GitHub OAuth 2.0 authorization endpoint",
    operation_id="github_login"
)
async def github_login():
    try:
        params = {
            "client_id": settings.github_client_id,
            "redirect_uri": settings.github_redirect_uri,
            "scope": "user:email",
            "allow_signup": "true",
        }
        url = f"{settings.github_auth_url}?{urlencode(params)}"
        logger.info("Redirecting to GitHub OAuth 2.0 authorization endpoint.")
        return RedirectResponse(url)
    except Exception as e:
        logger.error(f"Error during GitHub login redirection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during GitHub login redirection",
        )

@auth_router.get(
    "/auth/github/callback",
    tags=["Authentication 🔐"],
    description="Handle GitHub OAuth 2.0 callback",
    operation_id="github_callback"
)
async def github_callback(code: str, db: Session = Depends(get_db)):
    try:
        sso_handler = SSOLoginHandler(db)
        token_data = await sso_handler.exchange_github_code_for_token(code)
        github_user_info = await sso_handler.get_github_user_info(
            token_data["access_token"]
        )
        logger.info("GitHub OAuth 2.0 callback handled successfully.")
        return await sso_handler.handle_github_login(github_user_info)
    except Exception as e:
        logger.error(f"Error handling GitHub OAuth 2.0 callback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error handling GitHub OAuth 2.0 callback",
        )

@auth_router.post("/refresh", response_model=Token, tags=["Authentication 🔐"], description="Refresh access token", operation_id="refresh_access_token")
def refresh_access_token(refresh_token: str, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials")
    token_data = verify_token(refresh_token, credentials_exception)
    access_token = create_access_token(data={"sub": token_data.username})
    return {"access_token": access_token, "token_type": "bearer"}