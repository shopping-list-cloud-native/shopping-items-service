from uuid import UUID

import httpx
from fastapi import HTTPException, status

from app.config import settings


async def create_notification(user_id: UUID, list_id: UUID, message: str) -> None:
    async with httpx.AsyncClient(base_url=settings.notification_service_url, timeout=10.0) as client:
        response = await client.post(
            "/internal/notifications",
            json={
                "user_id": str(user_id),
                "list_id": str(list_id),
                "message": message,
            },
        )

    if response.is_error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Notification service failed to create notification",
        )
