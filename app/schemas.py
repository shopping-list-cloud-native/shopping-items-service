from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class CreateItemRequest(BaseModel):
    name: str
    quantity: int = 1
    estimated_price: Decimal = Decimal("0")


class UpdateItemRequest(BaseModel):
    name: str | None = None
    quantity: int | None = None
    estimated_price: Decimal | None = None
    checked: bool | None = None


class ItemResponse(BaseModel):
    id: UUID
    list_id: UUID
    name: str
    quantity: int
    estimated_price: Decimal
    checked: bool
    created_at: datetime
    updated_at: datetime


class DeleteItemResponse(BaseModel):
    message: str


class BudgetStatusResponse(BaseModel):
    list_id: UUID
    max_budget: Decimal
    current_total: Decimal
    remaining_budget: Decimal
    status: str


class ListRecipientResponse(BaseModel):
    user_id: UUID
    email: str
    role: Literal["owner", "editor", "viewer"]
