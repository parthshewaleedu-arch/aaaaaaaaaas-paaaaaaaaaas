"""Token Blacklist and Revocation Store.

Maintains revoked JWT access and refresh tokens to prevent replay attacks
and enforce immediate logout and token rotation.
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, Optional
import threading

_lock = threading.Lock()
# In-memory store: maps jti (or token) to expiration timestamp
_revoked_tokens: Dict[str, datetime] = {}


def blacklist_token(
    token_jti: str,
    expires_at: Optional[datetime] = None,
    expires_in_seconds: Optional[int] = None,
) -> None:
    """Add a JWT ID (jti) or token string to the blacklist."""
    if not token_jti:
        return
    with _lock:
        now = datetime.now(timezone.utc)
        if expires_in_seconds is not None:
            exp = now + timedelta(seconds=expires_in_seconds)
        elif expires_at is not None:
            exp = expires_at
        else:
            exp = now + timedelta(days=7)
        _revoked_tokens[token_jti] = exp


def is_token_blacklisted(token_jti: str) -> bool:
    """Check if a JWT ID (jti) or token string has been revoked."""
    if not token_jti:
        return False
    with _lock:
        if token_jti in _revoked_tokens:
            # Check if token expiration has already passed
            exp = _revoked_tokens[token_jti]
            now = datetime.now(timezone.utc)
            # Ensure timezone-aware comparison
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=timezone.utc)
            if now > exp:
                del _revoked_tokens[token_jti]
                return False
            return True
        return False


def clean_expired_tokens() -> int:
    """Prune expired tokens from the blacklist."""
    with _lock:
        now = datetime.now(timezone.utc)
        expired_keys = [
            k
            for k, exp in _revoked_tokens.items()
            if (exp.replace(tzinfo=timezone.utc) if exp.tzinfo is None else exp) < now
        ]
        for k in expired_keys:
            del _revoked_tokens[k]
        return len(expired_keys)


def clear_blacklist() -> None:
    """Clear all blacklisted tokens (used primarily for test isolation)."""
    with _lock:
        _revoked_tokens.clear()
