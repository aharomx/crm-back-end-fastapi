from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.core.dependencies import get_current_user, verify_ownership
from app.models.user import User
from app.schemas.order import (
    OrderCreate,
    OrderUpdate,
    OrderResponse,
    OrderCreateFromQuote,
    OrderItemCreate,
    OrderItemResponse
)
from app.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crea un nuevo pedido"""
    service = OrderService(db)
    
    try:
        order = await service.create_order(order_data, current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    response = OrderResponse.model_validate(order)
    response.user_email = order.user.email
    response.user_username = order.user.username
    response.client_company = order.client.company_name
    response.client_contact = order.client.contact_name
    
    if order.quote:
        response.quote_number = order.quote.quote_number
    
    return response

@router.post("/from-quote", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order_from_quote(
    order_data: OrderCreateFromQuote,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crea un pedido a partir de una cotización aceptada.
    La cotización debe tener status 'accepted'.
    """
    service = OrderService(db)
    
    try:
        order = await service.create_order_from_quote(
            order_data.quote_id,
            order_data,
            current_user.id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quote not found"
        )
    
    response = OrderResponse.model_validate(order)
    response.user_email = order.user.email
    response.user_username = order.user.username
    response.client_company = order.client.company_name
    response.client_contact = order.client.contact_name
    
    if order.quote:
        response.quote_number = order.quote.quote_number
    
    return response

@router.get("/", response_model=List[OrderResponse])
async def get_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    client_id: Optional[int] = None,
    status: Optional[str] = Query(None, pattern="^(draft|confirmed|in_progress|shipped|delivered|cancelled)$"),
    priority: Optional[str] = Query(None, pattern="^(low|medium|high)$"),
    search: Optional[str] = Query(None, min_length=1),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista todos los pedidos con filtros.
    """
    service = OrderService(db)
    orders, total = await service.get_orders(
        skip, limit, client_id, current_user.id,
        status, priority, search, start_date, end_date
    )
    
    response = []
    for order in orders:
        order_response = OrderResponse.model_validate(order)
        order_response.user_email = order.user.email
        order_response.user_username = order.user.username
        order_response.client_company = order.client.company_name
        order_response.client_contact = order.client.contact_name
        
        if order.quote:
            order_response.quote_number = order.quote.quote_number
        
        response.append(order_response)
    
    return response

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene un pedido específico por ID"""
    service = OrderService(db)
    order = await service.get_order(order_id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    await verify_ownership(order.user_id, current_user)
    
    response = OrderResponse.model_validate(order)
    response.user_email = order.user.email
    response.user_username = order.user.username
    response.client_company = order.client.company_name
    response.client_contact = order.client.contact_name
    
    if order.quote:
        response.quote_number = order.quote.quote_number
    
    return response

@router.get("/number/{order_number}", response_model=OrderResponse)
async def get_order_by_number(
    order_number: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene un pedido por su número"""
    service = OrderService(db)
    order = await service.get_order_by_number(order_number)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    await verify_ownership(order.user_id, current_user)
    
    response = OrderResponse.model_validate(order)
    response.user_email = order.user.email
    response.user_username = order.user.username
    response.client_company = order.client.company_name
    response.client_contact = order.client.contact_name
    
    if order.quote:
        response.quote_number = order.quote.quote_number
    
    return response

@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int,
    update_data: OrderUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualiza un pedido existente"""
    service = OrderService(db)
    
    existing = await service.get_order(order_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    await verify_ownership(existing.user_id, current_user)
    
    order = await service.update_order(order_id, update_data)
    
    response = OrderResponse.model_validate(order)
    response.user_email = order.user.email
    response.user_username = order.user.username
    response.client_company = order.client.company_name
    response.client_contact = order.client.contact_name
    
    if order.quote:
        response.quote_number = order.quote.quote_number
    
    return response

@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Elimina un pedido"""
    service = OrderService(db)
    
    existing = await service.get_order(order_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    await verify_ownership(existing.user_id, current_user)
    
    deleted = await service.delete_order(order_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete order"
        )
    
    return None

# --- Order Items Endpoints ---

@router.post("/{order_id}/items", response_model=OrderItemResponse, status_code=status.HTTP_201_CREATED)
async def add_order_item(
    order_id: int,
    item_data: OrderItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Agrega un item a un pedido"""
    service = OrderService(db)
    
    order = await service.get_order(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    await verify_ownership(order.user_id, current_user)
    
    updated_order = await service.add_item(order_id, item_data)
    if not updated_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Buscar el item agregado (el último)
    if updated_order.items:
        return updated_order.items[-1]
    
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to add item"
    )

@router.put("/items/{item_id}", response_model=OrderItemResponse)
async def update_order_item(
    item_id: int,
    update_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualiza un item de pedido"""
    service = OrderService(db)
    
    # Verificar que el item existe y el usuario tiene permisos
    result = await db.execute(
        select(OrderItem).where(OrderItem.id == item_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    order = await service.get_order(item.order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    await verify_ownership(order.user_id, current_user)
    
    updated_order = await service.update_item(item_id, update_data)
    if not updated_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    # Buscar el item actualizado
    for updated_item in updated_order.items:
        if updated_item.id == item_id:
            return updated_item
    
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to update item"
    )

@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_order_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Elimina un item de pedido"""
    service = OrderService(db)
    
    # Verificar que el item existe y el usuario tiene permisos
    result = await db.execute(
        select(OrderItem).where(OrderItem.id == item_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    order = await service.get_order(item.order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    await verify_ownership(order.user_id, current_user)
    
    await service.remove_item(item_id)
    return None

@router.get("/stats/dashboard", response_model=dict)
async def get_order_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene estadísticas de pedidos para el dashboard"""
    service = OrderService(db)
    stats = await service.get_stats(current_user.id)
    return stats