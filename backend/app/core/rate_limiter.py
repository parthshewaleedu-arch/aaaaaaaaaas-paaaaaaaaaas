"""Rate Limiting and Abuse Prevention.

Sliding window rate limiter to throttle authentication brute-force attacks,
spam review submissions, and resource flooding per Section 73 & 112.
"""

from collections import defaultdict
import threading
import time
from typing import Callable, Dict, List, Tuple

from fastapi import HTTPException, Request, status

from app.core.config import settings

_lock = threading.Lock()
# Maps bucket key -> list of float timestamps (epoch seconds)
_rate_limit_records: Dict[str, List[float]] = defaultdict(list)
_bypass_rate_limiting: bool = False


def set_rate_limit_bypass(bypass: bool) -> None:
    """Toggle rate limit bypass (primarily for unit testing)."""
    global _bypass_rate_limiting
    _bypass_rate_limiting = bypass


def clear_rate_limits() -> None:
    """Clear all recorded rate limit hits."""
    with _lock:
        _rate_limit_records.clear()


def check_rate_limit(
    key: str,
    limit: int,
    window_seconds: int,
) -> Tuple[bool, int, int]:
    """
    Check if an action is within rate limits using a sliding window.

    Returns:
        (is_allowed: bool, remaining_requests: int, retry_after_seconds: int)
    """
    if _bypass_rate_limiting or not getattr(settings, "RATE_LIMIT_ENABLED", True):
        return True, limit, 0

    now = time.time()
    window_start = now - window_seconds

    with _lock:
        timestamps = _rate_limit_records[key]
        # Prune timestamps outside current sliding window
        valid_timestamps = [ts for ts in timestamps if ts > window_start]
        _rate_limit_records[key] = valid_timestamps

        if len(valid_timestamps) >= limit:
            oldest = valid_timestamps[0]
            retry_after = max(1, int(oldest + window_seconds - now))
            return False, 0, retry_after

        valid_timestamps.append(now)
        remaining = limit - len(valid_timestamps)
        return True, remaining, 0


def rate_limit(
    limit: int = 60,
    window_seconds: int = 60,
    key_prefix: str = "general",
) -> Callable:
    """
    FastAPI dependency factory enforcing rate limits on endpoints.

    Args:
        limit: Maximum requests allowed within window.
        window_seconds: Sliding window span in seconds.
        key_prefix: Logical namespace (e.g. 'auth_login', 'reviews_create').
    """

    async def dependency(request: Request) -> None:
        # Determine client IP identifier
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        elif request.client and request.client.host:
            client_ip = request.client.host
        else:
            client_ip = "127.0.0.1"

        key = f"{key_prefix}:{client_ip}"
        allowed, remaining, retry_after = check_rate_limit(
            key=key,
            limit=limit,
            window_seconds=window_seconds,
        )

        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later.",
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                },
            )

    return dependency
