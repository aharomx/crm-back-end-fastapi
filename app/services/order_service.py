from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Tuple
from datetime import datetime
from app.repositories.order_repository import OrderRepository
from app.schemas.order import OrderCreate, OrderUpdate, OrderCreateFromQuote, OrderItemCreate
from app.models.order import Order
import random
import string

class OrderService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = OrderRepository(db)
    
    async def generate_order_number(self) -> str:
        """Genera un número único de pedido"""
        # Formato: O-YYYY-XXXXX
        year = datetime.now().year
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        return f"O-{year}-{random_part}"
    
    async def create_order(
        self,
        order_data: OrderCreate,
        user_id: int
    ) -> Order:
        """Crea un nuevo pedido"""
        # Validar fechas
        if order_data.delivery_date and order_data.delivery_date <= order_data.order_date:
            raise ValueError("Delivery date must be after order date")
        
        # Preparar datos
        data_dict = order_data.model_dump(exclude={'items'})
        data_dict["user_id"] = user_id
        data_dict["order_number"] = await self.generate_order_number()
        
        # Preparar items
        items_data = [item.model_dump() for item in order_data.items]
        
        return await self.repository.create(data_dict, items_data)
    
    async def create_order_from_quote(
        self,
        quote_id: int,
        order_data: OrderCreateFromQuote,
        user_id: int
    ) -> Optional[Order]:
        """Crea un pedido a partir de una cotización aceptada"""
        try:
            # Preparar datos
            data_dict = order_data.model_dump()
            data_dict["user_id"] = user_id
            data_dict["order_number"] = await self.generate_order_number()
            
            return await self.repository.create_from_quote(quote_id, data_dict)
        except ValueError as e:
            raise ValueError(str(e))
    
    async def get_order(self, order_id: int) -> Optional[Order]:
        """Obtiene un pedido por ID"""
        return await self.repository.get_by_id(order_id)
    
    async def get_order_by_number(self, order_number: str) -> Optional[Order]:
        """Obtiene un pedido por número"""
        return await self.repository.get_by_number(order_number)
    
    async def get_orders(
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
        """Obtiene lista de pedidos con filtros"""
        return await self.repository.get_all(
            skip, limit, client_id, user_id,
            status, priority, search, start_date, end_date
        )
    
    async def update_order(
        self,
        order_id: int,
        update_data: OrderUpdate
    ) -> Optional[Order]:
        """Actualiza un pedido"""
        update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
        if not update_dict:
            return await self.repository.get_by_id(order_id)
        return await self.repository.update(order_id, update_dict)
    
    async def delete_order(self, order_id: int) -> bool:
        """Elimina un pedido"""
        return await self.repository.delete(order_id)
    
    async def add_item(self, order_id: int, item_data: OrderItemCreate) -> Optional[Order]:
        """Agrega un item al pedido"""
        order = await self.get_order(order_id)
        if not order:
            return None
        
        await self.repository.add_item(order_id, item_data.model_dump())
        return await self.get_order(order_id)
    
    async def update_item(self, item_id: int, update_data: dict) -> Optional[Order]:
        """Actualiza un item del pedido"""
        item = await self.repository.update_item(item_id, update_data)
        if not item:
            return None
        return await self.get_order(item.order_id)
    
    async def remove_item(self, item_id: int) -> Optional[Order]:
        """Elimina un item del pedido"""
        result = await self.db.execute(
            select(OrderItem).where(OrderItem.id == item_id)
        )
        item = result.scalar_one_or_none()
        if not item:
            return None
        
        order_id = item.order_id
        await self.repository.remove_item(item_id)
        return await self.get_order(order_id)
    
    async def get_stats(self, user_id: Optional[int] = None) -> dict:
        """Obtiene estadísticas de pedidos"""
        return await self.repository.get_stats(user_id)