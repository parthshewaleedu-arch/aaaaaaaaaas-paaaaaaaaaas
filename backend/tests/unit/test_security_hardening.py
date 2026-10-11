"""Unit tests for Security Hardening, Token Rotation, Blacklisting, Rate Limiting, and Upload Validation.

Verifies:
1. Token revocation and in-memory blacklist.
2. Single-use refresh token rotation.
3. Logout token invalidation.
4. Sliding window rate limiter dependency & HTTP 429 response.
5. Defense-in-depth security headers (CSP, Permissions-Policy, X-Frame-Options, etc.).
6. HTML/XSS input sanitization.
7. Magic-byte image upload validation.
"""

import time
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.auth.dependencies import get_current_user
from app.auth.jwt_handler import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.config import settings
from app.core.database import get_db
from app.core.rate_limiter import (
    check_rate_limit,
    clear_rate_limits,
)
from app.core.sanitizer import sanitize_text, validate_image_upload
from app.core.token_blacklist import (
    blacklist_token,
    clean_expired_tokens,
    clear_blacklist,
    is_token_blacklisted,
)
from app.main import app
from app.models.user import User, UserRole, UserStatus


# =========================================================================
# 1. Token Blacklist & Expiration Tests
# =========================================================================


def test_token_blacklist_functionality():
    """Verify tokens can be blacklisted, checked, and cleared."""
    jti_1 = str(uuid4())
    jti_2 = str(uuid4())

    assert not is_token_blacklisted(jti_1)
    assert not is_token_blacklisted(jti_2)

    blacklist_token(jti_1, expires_in_seconds=60)
    assert is_token_blacklisted(jti_1)
    assert not is_token_blacklisted(jti_2)

    # Test clearing blacklist
    clear_blacklist()
    assert not is_token_blacklisted(jti_1)


def test_token_blacklist_expiry_cleanup():
    """Verify expired blacklisted tokens are cleaned up."""
    jti = str(uuid4())
    # Add with a 1-second TTL
    blacklist_token(jti, expires_in_seconds=1)
    assert is_token_blacklisted(jti)

    # Wait for expiration
    time.sleep(1.1)
    clean_expired_tokens()
    assert not is_token_blacklisted(jti)


def test_get_current_user_rejects_blacklisted_token():
    """Verify get_current_user dependency rejects a blacklisted access token with 401."""
    db_mock = MagicMock()
    user = User(
        id=uuid4(),
        email="student@mitaoe.ac.in",
        password_hash="hashed_pw",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    db_mock.query.return_value.filter.return_value.first.return_value = user

    token = create_access_token(data={"sub": user.email})
    payload = decode_token(token, settings.JWT_SECRET)
    assert payload is not None
    jti = payload["jti"]

    # Before blacklisting - works
    resolved_user = get_current_user(token=token, db=db_mock)
    assert resolved_user.email == user.email

    # Blacklist the token
    blacklist_token(jti)
    assert is_token_blacklisted(jti)

    # After blacklisting - raises 401
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token=token, db=db_mock)
    assert exc_info.value.status_code == 401
    assert "revoked" in exc_info.value.detail.lower()


# =========================================================================
# 2. Refresh Token Rotation Tests
# =========================================================================


def test_refresh_token_rotation_and_single_use():
    """Verify refresh token rotation issues new tokens and revokes the old refresh token."""
    client = TestClient(app)
    db_mock = MagicMock()

    user = User(
        id=uuid4(),
        email="test_refresh@mitaoe.ac.in",
        password_hash="hashed_pw",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    db_mock.query.return_value.filter.return_value.first.return_value = user

    def override_get_db():
        yield db_mock

    app.dependency_overrides[get_db] = override_get_db

    try:
        # Issue initial refresh token
        original_refresh_token = create_refresh_token(data={"sub": user.email})
        original_payload = decode_token(
            original_refresh_token, settings.JWT_REFRESH_SECRET
        )
        assert original_payload is not None
        old_jti = original_payload["jti"]

        # First refresh attempt - should succeed
        resp = client.post(
            "/api/v1/auth/refresh-token",
            json={"refresh_token": original_refresh_token},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        new_refresh_token = data["refresh_token"]
        assert new_refresh_token != original_refresh_token

        # Verify old refresh token JTI was blacklisted
        assert is_token_blacklisted(old_jti)

        # Second refresh attempt using OLD token - MUST FAIL with 401
        replay_resp = client.post(
            "/api/v1/auth/refresh-token",
            json={"refresh_token": original_refresh_token},
        )
        assert replay_resp.status_code == 401
        assert "revoked" in replay_resp.json()["detail"].lower()
    finally:
        app.dependency_overrides.clear()


# =========================================================================
# 3. Logout Token Revocation Tests
# =========================================================================


def test_logout_revokes_access_and_refresh_tokens():
    """Verify /logout invalidates the bearer access token and optional refresh token."""
    client = TestClient(app)
    db_mock = MagicMock()

    user = User(
        id=uuid4(),
        email="logout_user@mitaoe.ac.in",
        password_hash="hashed_pw",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    db_mock.query.return_value.filter.return_value.first.return_value = user

    def override_get_db():
        yield db_mock

    app.dependency_overrides[get_db] = override_get_db

    try:
        access_token = create_access_token(data={"sub": user.email})
        refresh_token = create_refresh_token(data={"sub": user.email})

        access_payload = decode_token(access_token, settings.JWT_SECRET)
        refresh_payload = decode_token(refresh_token, settings.JWT_REFRESH_SECRET)

        assert access_payload and "jti" in access_payload
        assert refresh_payload and "jti" in refresh_payload

        # Logout with tokens
        resp = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"refresh_token": refresh_token},
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

        # Verify both tokens are blacklisted
        assert is_token_blacklisted(access_payload["jti"])
        assert is_token_blacklisted(refresh_payload["jti"])

        # Subsequent call with the same access token must be rejected with 401
        protected_resp = client.get(
            "/api/v1/notifications/unread-count",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert protected_resp.status_code == 401
        assert "revoked" in protected_resp.json()["detail"].lower()
    finally:
        app.dependency_overrides.clear()


# =========================================================================
# 4. Rate Limiter Tests
# =========================================================================


def test_sliding_window_rate_limiter_algorithm():
    """Verify check_rate_limit calculates remaining counts and blocks after threshold."""
    clear_rate_limits()
    key = "test_rate_bucket"
    limit = 3
    window = 10

    # Request 1
    allowed, rem, retry = check_rate_limit(key, limit=limit, window_seconds=window)
    assert allowed is True
    assert rem == 2
    assert retry == 0

    # Request 2
    allowed, rem, retry = check_rate_limit(key, limit=limit, window_seconds=window)
    assert allowed is True
    assert rem == 1
    assert retry == 0

    # Request 3
    allowed, rem, retry = check_rate_limit(key, limit=limit, window_seconds=window)
    assert allowed is True
    assert rem == 0
    assert retry == 0

    # Request 4 - Exceeded limit!
    allowed, rem, retry = check_rate_limit(key, limit=limit, window_seconds=window)
    assert allowed is False
    assert rem == 0
    assert retry > 0


def test_rate_limiter_endpoint_returns_429():
    """Verify that an endpoint protected by rate_limit returns HTTP 429 when exhausted."""
    clear_rate_limits()
    client = TestClient(app)
    db_mock = MagicMock()
    # Mock user query to return None (invalid user)
    db_mock.query.return_value.filter.return_value.first.return_value = None

    def override_get_db():
        yield db_mock

    app.dependency_overrides[get_db] = override_get_db

    try:
        # Call /api/v1/auth/token 10 times (limit=10)
        for _ in range(10):
            client.post(
                "/api/v1/auth/token",
                data={"username": "fake@test.com", "password": "wrong"},
            )

        # 11th request MUST be 429 Too Many Requests
        resp = client.post(
            "/api/v1/auth/token",
            data={"username": "fake@test.com", "password": "wrong"},
        )
        assert resp.status_code == 429
        assert "Retry-After" in resp.headers
        assert resp.headers["X-RateLimit-Limit"] == "10"
        assert resp.headers["X-RateLimit-Remaining"] == "0"
    finally:
        app.dependency_overrides.clear()


# =========================================================================
# 5. Security Headers Tests
# =========================================================================


def test_security_headers_present_in_responses():
    """Verify standard security headers are present on all application responses."""
    client = TestClient(app)
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200

    headers = resp.headers
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-Frame-Options") == "DENY"
    assert headers.get("X-XSS-Protection") == "1; mode=block"
    assert "strict-origin-when-cross-origin" in headers.get("Referrer-Policy", "")
    assert "default-src 'self'" in headers.get("Content-Security-Policy", "")
    assert "geolocation=(self)" in headers.get("Permissions-Policy", "")
    assert "camera=()" in headers.get("Permissions-Policy", "")


# =========================================================================
# 6. HTML/XSS Input Sanitization Tests
# =========================================================================


def test_sanitize_text_removes_dangerous_html():
    """Verify sanitize_text removes script tags and dangerous HTML while preserving text."""
    # Script tag
    malicious = "<script>alert('pwned')</script>Great food!"
    cleaned = sanitize_text(malicious)
    assert "<script>" not in cleaned
    assert "alert" not in cleaned
    assert "Great food!" in cleaned

    # Image with onerror payload
    img_xss = '<img src="x" onerror="alert(1)">Tasty breakfast!'
    cleaned = sanitize_text(img_xss)
    assert "onerror" not in cleaned
    assert "<img" not in cleaned
    assert "Tasty breakfast!" in cleaned

    # Anchor with javascript: href
    js_link = '<a href="javascript:void(0)">Click here</a>'
    cleaned = sanitize_text(js_link)
    assert "javascript:" not in cleaned

    # Plain text remains unchanged
    plain = "Excellent student discount and clean environment."
    assert sanitize_text(plain) == plain


# =========================================================================
# 7. Image Upload Magic-Byte Validation Tests
# =========================================================================


def test_validate_image_upload_magic_bytes():
    """Verify validate_image_upload allows genuine image formats and rejects spoofing."""
    # Valid JPEG
    jpeg_bytes = b"\xFF\xD8\xFF\xE0" + b"\x00" * 100
    is_valid, err = validate_image_upload(jpeg_bytes, "photo.jpg", "image/jpeg")
    assert is_valid is True
    assert err is None

    # Valid PNG
    png_bytes = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
    is_valid, err = validate_image_upload(png_bytes, "image.png", "image/png")
    assert is_valid is True
    assert err is None

    # Valid WEBP
    webp_bytes = b"RIFF\x00\x00\x00\x00WEBP" + b"\x00" * 100
    is_valid, err = validate_image_upload(webp_bytes, "avatar.webp", "image/webp")
    assert is_valid is True
    assert err is None

    # Invalid extension (.exe)
    is_valid, err = validate_image_upload(png_bytes, "exploit.exe", "image/png")
    assert is_valid is False
    assert err is not None
    assert "extension" in err.lower()

    # Extension .png but content is executable / text script
    is_valid, err = validate_image_upload(
        b"<?php echo 'attack'; ?>", "trojan.png", "image/png"
    )
    assert is_valid is False
    assert err is not None
    assert "signature" in err.lower()

    # Oversized image exceeding MAX_IMAGE_SIZE
    huge_bytes = b"\xFF\xD8\xFF\xE0" + (b"\x00" * (6 * 1024 * 1024))
    is_valid, err = validate_image_upload(huge_bytes, "large.jpg", "image/jpeg")
    assert is_valid is False
    assert err is not None
    assert "exceeds" in err.lower()

    # Invalid MIME type
    is_valid, err = validate_image_upload(jpeg_bytes, "photo.jpg", "text/plain")
    assert is_valid is False
    assert err is not None
    assert "content type" in err.lower()
