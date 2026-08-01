import secrets
from typing import Annotated

from app.config import settings
from fastapi import Header, HTTPException, status


async def require_admin_key(
    x_admin_key: Annotated[str | None, Header()] = None,
) -> None:
    """Protect administrative routes with an environment-provided API key."""

    configured_key = settings.ADMIN_API_KEY
    if not configured_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Administrative actions are disabled until ADMIN_API_KEY is configured.",
        )

    if not x_admin_key or not secrets.compare_digest(x_admin_key, configured_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-Admin-Key header.",
        )
