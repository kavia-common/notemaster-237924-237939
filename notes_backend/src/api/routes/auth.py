from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.api.core.auth import create_access_token, hash_password, verify_password
from src.api.core.db import get_db
from src.api.deps import get_current_user
from src.api.models import User
from src.api.schemas import AuthLoginRequest, AuthRegisterRequest, TokenResponse, UserMeResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=TokenResponse,
    summary="Register a new user",
    description="Create an account with email+password and return a JWT access token.",
    operation_id="auth_register",
)
def register(payload: AuthRegisterRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Register a new user and return an access token."""
    email = payload.email.strip().lower()
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    existing = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(email=email, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)

    return TokenResponse(access_token=create_access_token(user_id=user.id, email=user.email))


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login",
    description="Authenticate with email+password and return a JWT access token.",
    operation_id="auth_login",
)
def login(payload: AuthLoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Login a user and return an access token."""
    email = payload.email.strip().lower()
    user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    return TokenResponse(access_token=create_access_token(user_id=user.id, email=user.email))


@router.get(
    "/me",
    response_model=UserMeResponse,
    summary="Get current user",
    description="Returns the currently authenticated user.",
    operation_id="auth_me",
)
def me(user: User = Depends(get_current_user)) -> UserMeResponse:
    """Return the authenticated user's profile."""
    return UserMeResponse(id=user.id, email=user.email)
