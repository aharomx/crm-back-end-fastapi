from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import Optional, List, Tuple
from datetime import datetime
from app.models.order import Order, OrderItem
from app.models.quote import Quote, QuoteItem
from app.models.client import Client

class OrderRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, order_data: dict, items_data: List[dict]) -> Order:
        """Crea un nuevo pedido con sus items"""
        # Crear el pedido
        order = Order(**order_data)
        self.db.add(order)
        await self.db.flush()  # Para obtener el ID
        
        # Crear los items
        for item_data in items_data:
            item = OrderItem(order_id=order.id, **item_data)
            self.db.add(item)
        
        # Recalcular totales
        await self._recalculate_totals(order)
        
        await self.db.commit()
        await self.db.refresh(order)
        return order
    
    async def create_from_quote(self, quote_id: int, order_data: dict) -> Optional[Order]:
        """Crea un pedido a partir de una cotización aceptada"""
        # Obtener la cotización
        result = await self.db.execute(
            select(Quote)
            .where(Quote.id == quote_id)
            .options(selectinload(Quote.items))
        )
        quote = result.scalar_one_or_none()
        
        if not quote:
            return None
        
        # Validar que la cotización esté aceptada
        if quote.status != 'accepted':
            raise ValueError("Quote must be accepted before creating an order")
        
        # Validar que la cotización tenga un cliente
        if not quote.client_id:
            raise ValueError("Quote must have a client to create an order")
        
        # Crear el pedido
        order_dict = {
            "client_id": quote.client_id,
            "quote_id": quote.id,
            "order_date": datetime.now(),
            "delivery_date": order_data.get("delivery_date"),
            "priority": order_data.get("priority", "medium"),
            "notes": order_data.get("notes"),
            "shipping_address": order_data.get("shipping_address"),
            "status": "confirmed"
        }
        
        order = Order(**order_dict)
        self.db.add(order)
        await self.db.flush()
        
        # Copiar items de la cotización
        for quote_item in quote.items:
            order_item = OrderItem(
                order_id=order.id,
                description=quote_item.description,
                quantity=quote_item.quantity,
                unit_price=quote_item.unit_price,
                discount=quote_item.discount,
                total=quote_item.total,
                quote_item_id=quote_item.id
            )
            self.db.add(order_item)
        
        # Recalcular totales
        await self._recalculate_totals(order)
        
        await self.db.commit()
        await self.db.refresh(order)
        return order
    
    async def get_by_id(self, order_id: int) -> Optional[Order]:
        """Obtiene un pedido por ID con sus items"""
        result = await self.db.execute(
            select(Order)
            .where(Order.id == order_id)
            .options(selectinload(Order.user))
            .options(selectinload(Order.client))
            .options(selectinload(Order.quote))
            .options(selectinload(Order.items))
        )
        return result.scalar_one_or_none()
    
    async def get_by_number(self, order_number: str) -> Optional[Order]:
        """Obtiene un pedido por número"""
        result = await self.db.execute(
            select(Order)
            .where(Order.order_number == order_number)
            .options(selectinload(Order.user))
            .options(selectinload(Order.client))
            .options(selectinload(Order.quote))
            .options(selectinload(Order.items))
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        client_id: Optional[int] = None,
        user_id: Optional[int] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        search: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Tuple[List[Order], int]:
        """Obtiene todos los pedidos con filtros"""
        query = select(Order).options(
            selectinload(Order.user),
            selectinload(Order.client),
            selectinload(Order.quote),
            selectinload(Order.items)
        )
        
        # Filtros
        filters = []
        
        if client_id:
            filters.append(Order.client_id == client_id)
        
        if user_id:
            filters.append(Order.user_id == user_id)
        
        if status:
            filters.append(Order.status == status)
        
        if priority:
            filters.append(Order.priority == priority)
        
        if search:
            search_term = f"%{search}%"
            filters.append(
                or_(
                    Order.order_number.ilike(search_term),
                    Order.notes.ilike(search_term)
                )
            )
        
        if start_date:
            filters.append(Order.created_at >= start_date)
        
        if end_date:
            filters.append(Order.created_at <= end_date)
        
        if filters:
            query = query.where(and_(*filters))
        
        # Contar total
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.execute(count_query)
        total_count = total.scalar()
        
        # Paginación y orden
        query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        
        return result.scalars().all(), total_count
    
    async def update(self, order_id: int, update_data: dict) -> Optional[Order]:
        """Actualiza un pedido"""
        order = await self.get_by_id(order_id)
        if not order:
            return None
        
        for key, value in update_data.items():
            if value is not None and hasattr(order, key):
                setattr(order, key, value)
        
        await self.db.commit()
        await self.db.refresh(order)
        return order
    
    async def delete(self, order_id: int) -> bool:
        """Elimina un pedido"""
        order = await self.get_by_id(order_id)
        if not order:
            return False
        
        await self.db.delete(order)
        await self.db.commit()
        return True
    
    async def update_item(self, item_id: int, update_data: dict) -> Optional[OrderItem]:
        """Actualiza un item de pedido"""
        result = await self.db.execute(
            select(OrderItem).where(OrderItem.id == item_id)
        )
        item = result.scalar_one_or_none()
        if not item:
            return None
        
        for key, value in update_data.items():
            if value is not None and hasattr(item, key):
                setattr(item, key, value)
        
        await self.db.commit()
        await self.db.refresh(item)
        
        # Recalcular totales del pedido
        order = await self.get_by_id(item.order_id)
        if order:
            await self._recalculate_totals(order)
            await self.db.commit()
        
        return item
    
    async def add_item(self, order_id: int, item_data: dict) -> Optional[OrderItem]:
        """Agrega un item a un pedido"""
        order = await self.get_by_id(order_id)
        if not order:
            return None
        
        item = OrderItem(order_id=order_id, **item_data)
        self.db.add(item)
        
        await self._recalculate_totals(order)
        await self.db.commit()
        await self.db.refresh(item)
        return item
    
    async def remove_item(self, item_id: int) -> bool:
        """Elimina un item de pedido"""
        result = await self.db.execute(
            select(OrderItem).where(OrderItem.id == item_id)
        )
        item = result.scalar_one_or_none()
        if not item:
            return False
        
        order_id = item.order_id
        
        await self.db.delete(item)
        
        # Recalcular totales del pedido
        order = await self.get_by_id(order_id)
        if order:
            await self._recalculate_totals(order)
        
        await self.db.commit()
        return True
    
    async def _recalculate_totals(self, order: Order):
        """Recalcula los totales de un pedido"""
        # Cargar items si no están cargados
        if not hasattr(order, 'items') or not order.items:
            result = await self.db.execute(
                select(OrderItem).where(OrderItem.order_id == order.id)
            )
            order.items = result.scalars().all()
        
        # Calcular subtotal
        subtotal = 0.0
        for item in order.items:
            # Calcular total del item
            item.total = (item.quantity * item.unit_price) - item.discount
            if item.total < 0:
                item.total = 0
            subtotal += item.total
        
        order.subtotal = subtotal
        order.total = subtotal + order.tax - order.discount
        if order.total < 0:
            order.total = 0
    
    async def get_stats(self, user_id: Optional[int] = None) -> dict:
        """Obtiene estadísticas de pedidos"""
        query = select(Order)
        
        if user_id:
            query = query.where(Order.user_id == user_id)
        
        # Total de pedidos
        total_result = await self.db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = total_result.scalar()
        
        # Por status
        status_query = select(Order.status, func.count()).group_by(Order.status)
        if user_id:
            status_query = status_query.where(Order.user_id == user_id)
        status_result = await self.db.execute(status_query)
        by_status = {status: count for status, count in status_result.all()}
        
        # Por prioridad
        priority_query = select(Order.priority, func.count()).group_by(Order.priority)
        if user_id:
            priority_query = priority_query.where(Order.user_id == user_id)
        priority_result = await self.db.execute(priority_query)
        by_priority = {priority: count for priority, count in priority_result.all()}
        
        # Total en pedidos (suma de totales)
        total_value_query = select(func.sum(Order.total))
        if user_id:
            total_value_query = total_value_query.where(Order.user_id == user_id)
        total_value_result = await self.db.execute(total_value_query)
        total_value = total_value_result.scalar() or 0.0
        
        # Pedidos entregados (suma)
        delivered_value_query = select(func.sum(Order.total)).where(Order.status == 'delivered')
        if user_id:
            delivered_value_query = delivered_value_query.where(Order.user_id == user_id)
        delivered_value_result = await self.db.execute(delivered_value_query)
        delivered_value = delivered_value_result.scalar() or 0.0
        
        return {
            "total": total,
            "by_status": by_status,
            "by_priority": by_priority,
            "total_value": float(total_value),
            "delivered_value": float(delivered_value)
        }