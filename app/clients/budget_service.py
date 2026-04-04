from uuid import UUID

import httpx
from fastapi import HTTPException

from app.config import settings
from app.schemas import BudgetStatusResponse


async def recalculate_budget(list_id: UUID) -> BudgetStatusResponse:
    async with httpx.AsyncClient(base_url=settings.budget_service_url, timeout=10.0) as client:
        response = await client.post(f"/internal/lists/{list_id}/budget/recalculate")

    if response.is_error:
        raise HTTPException(status_code=502, detail="Budget service failed to recalculate budget")

    return BudgetStatusResponse.model_validate(response.json())
