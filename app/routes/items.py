from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, status

from app.clients.budget_service import recalculate_budget
from app.clients.io_service import (
    create_item,
    delete_item,
    get_items,
    get_list_recipients,
    update_item,
)
from app.clients.notification_service import create_notification
from app.schemas import CreateItemRequest, DeleteItemResponse, ItemResponse, UpdateItemRequest

router = APIRouter(prefix="/internal", tags=["items"])


@router.post("/lists/{list_id}/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item_endpoint(
    payload: CreateItemRequest,
    list_id: UUID,
    x_user_id: str = Header(...),
    x_user_email: str = Header(...),
) -> ItemResponse:
    created = await create_item(
        list_id=list_id,
        name=payload.name,
        quantity=payload.quantity,
        estimated_price=payload.estimated_price,
    )
    recipients = await get_list_recipients(list_id)
    for recipient in recipients:
        if str(recipient.user_id) != x_user_id:
            await create_notification(
                user_id=recipient.user_id,
                list_id=list_id,
                message=f"{x_user_email} a adaugat item-ul {created.name}.",
            )
    await recalculate_budget(list_id)
    return ItemResponse.model_validate(created.model_dump())


@router.get("/lists/{list_id}/items", response_model=list[ItemResponse])
async def get_items_endpoint(list_id: UUID) -> list[ItemResponse]:
    items = await get_items(list_id=list_id)
    return [ItemResponse.model_validate(item.model_dump()) for item in items]


@router.patch("/lists/{list_id}/items/{item_id}", response_model=ItemResponse)
async def update_item_endpoint(
    payload: UpdateItemRequest,
    list_id: UUID,
    item_id: UUID,
    x_user_id: str = Header(...),
    x_user_email: str = Header(...),
) -> ItemResponse:
    updated = await update_item(
        item_id=item_id,
        list_id=list_id,
        name=payload.name,
        quantity=payload.quantity,
        estimated_price=payload.estimated_price,
        checked=payload.checked,
    )
    if payload.checked is True:
        recipients = await get_list_recipients(list_id)
        for recipient in recipients:
            if str(recipient.user_id) != x_user_id:
                await create_notification(
                    user_id=recipient.user_id,
                    list_id=list_id,
                    message=f"{x_user_email} a bifat item-ul {updated.name}.",
                )
    await recalculate_budget(list_id)
    return ItemResponse.model_validate(updated.model_dump())


@router.delete("/lists/{list_id}/items/{item_id}", response_model=DeleteItemResponse)
async def delete_item_endpoint(list_id: UUID, item_id: UUID) -> DeleteItemResponse:
    deleted = await delete_item(item_id=item_id, list_id=list_id)
    await recalculate_budget(list_id)
    return DeleteItemResponse.model_validate(deleted.model_dump())
