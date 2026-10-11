"""Authentication router with refresh token rotation and revocation."""

from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user, oauth2_scheme
from app.auth.jwt_handler import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.core.config import settings
from app.core.database import get_db
from app.core.rate_limiter import rate_limit
from app.core.token_blacklist import blacklist_token, is_token_blacklisted
from app.models.user import User

router = APIRouter()


class RefreshTokenRequest(BaseModel):
    """Payload to refresh expired access token."""

    refresh_token: str


class LogoutRequest(BaseModel):
    """Optional payload during logout to also invalidate refresh token."""

    refresh_token: Optional[str] = None


@router.post(
    "/token",
    summary="Login for access token",
    dependencies=[Depends(rate_limit(limit=10, window_seconds=60, key_prefix="login"))],
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    OAuth2 compatible token login.
    Returns access token and refresh token with unique jti identifiers.
    """
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": user.email})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post(
    "/refresh-token",
    summary="Refresh and rotate access token",
    dependencies=[
        Depends(rate_limit(limit=20, window_seconds=60, key_prefix="refresh"))
    ],
)
async def refresh_token(
    refresh_token: Optional[str] = Query(None),
    body: Optional[RefreshTokenRequest] = None,
    db: Session = Depends(get_db),
):
    """
    Refresh and rotate access token.
    Enforces single-use refresh token rotation and blacklists previous refresh token.
    """
    token_str = (body.refresh_token if body else None) or refresh_token
    if not token_str:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token required",
        )

    payload = decode_token(token_str, settings.JWT_REFRESH_SECRET)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    old_jti = payload.get("jti")
    if old_jti and is_token_blacklisted(old_jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    # Invalidate previous refresh token (Rotation!)
    if old_jti:
        blacklist_token(old_jti)

    # Issue new access token and rotated refresh token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    new_refresh_token = create_refresh_token(data={"sub": user.email})

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


@router.post(
    "/logout",
    summary="Logout and revoke active tokens",
    dependencies=[
        Depends(rate_limit(limit=20, window_seconds=60, key_prefix="logout"))
    ],
)
async def logout(
    body: Optional[LogoutRequest] = None,
    current_user: User = Depends(get_current_active_user),
    token: str = Depends(oauth2_scheme),
):
    """
    Invalidate the current access token and optional refresh token immediately.
    """
    # Blacklist current access token
    access_payload = decode_token(token, settings.JWT_SECRET)
    if access_payload and access_payload.get("jti"):
        blacklist_token(access_payload.get("jti"))

    # Blacklist client refresh token if provided
    if body and body.refresh_token:
        refresh_payload = decode_token(body.refresh_token, settings.JWT_REFRESH_SECRET)
        if refresh_payload and refresh_payload.get("jti"):
            blacklist_token(refresh_payload.get("jti"))

    return {
        "success": True,
        "message": "Successfully logged out",
    }
