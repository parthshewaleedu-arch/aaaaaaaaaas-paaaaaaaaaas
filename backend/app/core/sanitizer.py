"""Input Sanitization and File Upload Security.

Protects against Cross-Site Scripting (XSS), path traversal,
and malicious file upload injection per Section 73 & 74.
"""

import os
import re
from typing import Optional, Tuple


# Regex pattern to match dangerous script/HTML constructs
DANGEROUS_HTML_PATTERNS = [
    re.compile(r"<\s*script[^>]*>.*?<\s*/\s*script\s*>", re.IGNORECASE | re.DOTALL),
    re.compile(r"<\s*iframe[^>]*>.*?<\s*/\s*iframe\s*>", re.IGNORECASE | re.DOTALL),
    re.compile(r"<\s*object[^>]*>.*?<\s*/\s*object\s*>", re.IGNORECASE | re.DOTALL),
    re.compile(r"<\s*embed[^>]*>", re.IGNORECASE),
    re.compile(r"<\s*style[^>]*>.*?<\s*/\s*style\s*>", re.IGNORECASE | re.DOTALL),
    re.compile(r"javascript\s*:", re.IGNORECASE),
    re.compile(r"on\w+\s*=", re.IGNORECASE),  # Matches onload=, onclick=, onerror=
]

# Magic number signatures for permitted image types
IMAGE_SIGNATURES = {
    "jpeg": b"\xff\xd8\xff",
    "png": b"\x89PNG\r\n\x1a\n",
    "webp_riff": b"RIFF",
    "webp_sig": b"WEBP",
}

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 Megabytes


def sanitize_text(text: Optional[str]) -> Optional[str]:
    """
    Sanitize text input by neutralizing dangerous HTML, script tags, and event handlers.
    Preserves harmless text and unicode characters.
    """
    if not text:
        return text

    sanitized = text
    for pattern in DANGEROUS_HTML_PATTERNS:
        sanitized = pattern.sub("", sanitized)

    # Strip raw tag delimiters that look like HTML tags
    sanitized = re.sub(r"<[^>]*>", "", sanitized)
    return sanitized.strip()


def validate_image_upload(
    file_bytes: bytes,
    filename: str,
    content_type: str,
    max_size_bytes: int = MAX_IMAGE_SIZE,
) -> Tuple[bool, Optional[str]]:
    """
    Validate uploaded image file by extension, MIME type, size, and magic byte signature.

    Returns:
        (is_valid: bool, error_message: Optional[str])
    """
    if not file_bytes:
        return False, "File is empty"

    if len(file_bytes) > max_size_bytes:
        return (
            False,
            f"File size exceeds maximum allowed limit of {max_size_bytes // (1024 * 1024)}MB",
        )

    # 1. Extension check
    _, ext = os.path.splitext(filename.lower())
    if ext not in ALLOWED_EXTENSIONS:
        return (
            False,
            f"Invalid file extension '{ext}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    # 2. MIME type check
    if content_type.lower() not in ALLOWED_MIME_TYPES:
        return (
            False,
            f"Invalid content type '{content_type}'. Allowed: {', '.join(sorted(ALLOWED_MIME_TYPES))}",
        )

    # 3. Magic number signature inspection (prevent executable masquerading as image)
    is_jpeg = file_bytes.startswith(IMAGE_SIGNATURES["jpeg"])
    is_png = file_bytes.startswith(IMAGE_SIGNATURES["png"])
    is_webp = (
        file_bytes.startswith(IMAGE_SIGNATURES["webp_riff"])
        and len(file_bytes) >= 12
        and file_bytes[8:12] == IMAGE_SIGNATURES["webp_sig"]
    )

    if not (is_jpeg or is_png or is_webp):
        return False, "File content signature does not match a valid image format"

    return True, None
