from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.core.dependencies import get_current_user, verify_ownership
from app.models.user import User
from app.schemas.quote import (
    QuoteCreate,
    QuoteUpdate,
    QuoteResponse,
    QuoteItemCreate,
    QuoteItemResponse
)
from app.services.quote_service import QuoteService

router = APIRouter(prefix="/quotes", tags=["Quotes"])

@router.post("/", response_model=QuoteResponse, status_code=status.HTTP_201_CREATED)
async def create_quote(
    quote_data: QuoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """ 
        Crea una nueva cotización.
        Debe estar asociada a un prospecto o a un cliente
    """

    service = QuoteService(db)

    try:
        quote = await service.create_quote(quote_data, current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    response = QuoteResponse.model_validate(quote)
    response.user_email = quote.user.email
    response.user_username = quote.user.username

    if quote.prospect:
        response.prospect_company = quote.prospect.company_name
        response.prospect_contact = quote.prospect.contact_name

    if quote.client:
        response.client_company = quote.client.company_name
        response.client_contact = quote.client.contact_name

    return response

@router.get("/", response_model=List[QuoteResponse])
async def get_quotes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    prospect_id: Optional[int] = None,
    client_id: Optional[int] = None,
    status: Optional[str] = Query(None, pattern="^(draft|sent|accepted|rejected|expired)$"),
    search: Optional[str] = Query(None, min_length=1),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """ Lista todas las cotizaciones con filtros """

    service = QuoteService(db)

    quotes, total = await service.get_quotes(
        skip, limit, prospect_id, client_id, current_user.id,
        status, search, start_date, end_date
    )

    response = []
    for quote in quotes:
        quote_response = QuoteResponse.model_validate(quote)
        quote_response.user_email = quote.user.email
        quote_response.user_username = quote.user.username

        if quote.prospect:
            quote_response.prospect_company = quote.prospect.company_name
            quote_response.prospect_company = quote.prospect.contact_name

        if quote.client:
            quote_response.client_company = quote.client.company_name
            quote_response.client_contact = quote.client.contact_name

        response.append(quote_response)

    return response

@router.get("/{quote_id}", response_model=QuoteResponse)
async def get_quote(
    quote_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """ Obtiene una cotización específica por ID """

    service = QuoteService(db)
    quote = await service.get_quote(quote_id)

    if not quote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quote not found"
        )

    await verify_ownership(quote.user_id, current_user)

    response = QuoteResponse.model_validate(quote)
    response.user_email = quote.user.email
    response.user_username = quote.user.username

    if quote.prospect:
        response.prospect_company = quote.prospect.company_name
        response.prospect_contact = quote.prospect.contact_name

    if quote.client:
        response.client_company = quote.client.company_name
        response.client_contact = quote.client.contact_name

    return response

@router.get("/number/{quote_number}", response_model=QuoteResponse)
async def get_quote_by_number(
    quote_number: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """ Obtiene una cotización por su numero """

    service = QuoteService(db)
    quote = await service.get_quote_by_number(quote_number)

    if not quote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quote not found"
        )

    await verify_ownership(quote.user_id, current_user)

    response = QuoteResponse.model_validate(quote)
    response.user_email = quote.user.email
    response.user_username = quote.user.username

    if quote.prospect:
        response.prospect_company = quote.prospect.company_name
        response.prospect_contact = quote.prospect.contact_name

    if quote.client:
        response.client_company = quote.client.company_name
        response.client_contact = quote.client.contact_name

    return response

@router.put("/{quote_id}", response_model=QuoteResponse)
async def update_quote(
    quote_id: int,
    update_data: QuoteUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: AsyncSession = Depends(get_current_user)
):
    """ Actualiza una cotización existente """

    service = QuoteService(db)

    existing = await service.get_quote(quote_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quote not found"
        )

    await verify_ownership(existing.user_id, current_user)

    quote = await service.update_quote(quote_id, update_data)

    response = QuoteResponse.model_validate(quote)
    response.user_email = quote.user.email
    response.user_username = quote.user.username

    if quote.prospect:
        response.prospect_company = quote.prospect.company_name
        response.prospect_contact = quote.prospect.contact_name

    if quote.client:
        response.client_company = quote.client.company_name
        response.client_contact = quote.client.contact_name

    return response

@router.delete("/{quote_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quote(
    quote_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """ Elimina una cotización """

    service = QuoteService(db)

    existing = await service.get_quote(quote_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quote not found"
        )

    await verify_ownership(existing.user_id, current_user)

    deleted = await service.delete_quote(quote_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete quote"
        )

    return None

# --------- Quote Items Endpoints ----

@router.post("/{quote_id}/items", response_model=QuoteItemResponse, status_code=status.HTTP_201_CREATED)
async def add_quote_item(
    quote_id: int,
    item_data: QuoteItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """ Agrega un item a una cotización """

    service = QuoteService(db)

    quote = await service.get_quote(quote_id)
    if not quote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quote not found"
        )

    await verify_ownership(quote.user_id, current_user)

    updated_quote = await service.add_item(quote_id, item_data)
    if not update_quote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quote not found"
        )

    # Buscar el item agregado (el último)
    if updated_quote.items:
        return updated_quote.items[-1]

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail= "Failed ti add item"
    )

@router.put("/items/{item_id}", response_model=QuoteResponse)
async def update_quote_item(
    item_id: int,
    update_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """ Actualiza un item de cotización """
    service = QuoteService(db)

    # Verificar que el item existe y el usuario tiene permisos
    result = await db.execute(
        select(QuoteItem).where(QuoteItem.id == item_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )

    quote = await service.get_quote(item.quote_id)
    if not quote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quote not found"
        )

    await verify_ownership(quote.user_id, current_user)

    updated_quote = await service.update_item(item_id, update_data)
    if not updated_quote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )

    # Buscar el item actualizado
    for updated_item in updated_quote.items:
        if updated_item.id == item_id:
            return updated_item

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to update item"
    )

@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_quote_item(
    item_id:int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """ Elimina un item de cotización """
    service = QuoteService(db)

    # Verificar que el item existe y el usuario tiene permisos
    result = await db.execute(
        select(QuoteItem).where(QuoteItem.id == item_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )

    quote = await service.get_quote(item.quote_id)
    if not quote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quote not found"
        )

    await verify_ownership(quote.user_id, current_user)

    await service.remove_item(item_id)

    return None

@router.get("/stats/dashboard", response_model=dict)
async def get_quote_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """ Obtiene estadísticas de cotizaciones para el dashboard """

    service = QuoteService(db)
    stats = await service.get_stats(current_user.id)

    return stats

