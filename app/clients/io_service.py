from uuid import UUID

import httpx
from fastapi import HTTPException, status

from app.config import settings
from app.schemas import DeleteItemResponse, ItemResponse, ListRecipientResponse


def _serialize_decimal(value: str | int | float | None) -> str | int | float | None:
    if value is None:
        return None
    return str(value)


async def create_item(
    list_id: UUID,
    name: str,
    quantity: int,
    estimated_price: str | int | float,
) -> ItemResponse:
    async with httpx.AsyncClient(base_url=settings.io_service_url, timeout=10.0) as client:
        response = await client.post(
            "/internal/items",
            json={
                "list_id": str(list_id),
                "name": name,
                "quantity": quantity,
                "estimated_price": _serialize_decimal(estimated_price),
            },
        )

    if response.is_error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="IO service failed to create item",
        )

    return ItemResponse.model_validate(response.json())


async def get_items(list_id: UUID) -> list[ItemResponse]:
    async with httpx.AsyncClient(base_url=settings.io_service_url, timeout=10.0) as client:
        response = await client.get("/internal/items", params={"list_id": str(list_id)})

    if response.is_error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="IO service failed to fetch items",
        )

    return [ItemResponse.model_validate(item) for item in response.json()]


async def update_item(
    item_id: UUID,
    list_id: UUID,
    name: str | None,
    quantity: int | None,
    estimated_price: str | int | float | None,
    checked: bool | None,
) -> ItemResponse:
    async with httpx.AsyncClient(base_url=settings.io_service_url, timeout=10.0) as client:
        response = await client.patch(
            f"/internal/items/{item_id}",
            json={
                "list_id": str(list_id),
                "name": name,
                "quantity": quantity,
                "estimated_price": _serialize_decimal(estimated_price),
                "checked": checked,
            },
        )

    if response.status_code == status.HTTP_404_NOT_FOUND:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )

    if response.status_code == status.HTTP_400_BAD_REQUEST:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field must be provided for update",
        )

    if response.is_error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="IO service failed to update item",
        )

    return ItemResponse.model_validate(response.json())


async def delete_item(item_id: UUID, list_id: UUID) -> DeleteItemResponse:
    async with httpx.AsyncClient(base_url=settings.io_service_url, timeout=10.0) as client:
        response = await client.request(
            "DELETE",
            f"/internal/items/{item_id}",
            params={"list_id": str(list_id)},
        )

    if response.status_code == status.HTTP_404_NOT_FOUND:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )

    if response.is_error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="IO service failed to delete item",
        )

    return DeleteItemResponse.model_validate(response.json())


async def get_list_recipients(list_id: UUID) -> list[ListRecipientResponse]:
    async with httpx.AsyncClient(base_url=settings.io_service_url, timeout=10.0) as client:
        response = await client.get(f"/internal/list-members/by-list/{list_id}/recipients")

    if response.status_code == status.HTTP_404_NOT_FOUND:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="List not found",
        )

    if response.is_error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="IO service failed to fetch list recipients",
        )

    return [ListRecipientResponse.model_validate(item) for item in response.json()]
