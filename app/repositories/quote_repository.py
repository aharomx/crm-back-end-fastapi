from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import Optional, List, Tuple
from datetime import datetime
from app.models.quote import Quote, QuoteItem

class QuoteRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, quote_data: dict, items_data: List[dict]) -> Quote:
        """Crea una nueva cotización con sus items"""
        # Crear la cotización
        quote = Quote(**quote_data)
        self.db.add(quote)
        await self.db.flush()  # Para obtener el ID
        
        # Crear los items
        for item_data in items_data:
            item = QuoteItem(quote_id=quote.id, **item_data)
            self.db.add(item)
        
        # Recalcular totales
        await self._recalculate_totals(quote)
        
        await self.db.commit()
        await self.db.refresh(quote)
        return quote
    
    async def get_by_id(self, quote_id: int) -> Optional[Quote]:
        """Obtiene una cotización por ID con sus items"""
        result = await self.db.execute(
            select(Quote)
            .where(Quote.id == quote_id)
            .options(selectinload(Quote.user))
            .options(selectinload(Quote.prospect))
            .options(selectinload(Quote.client))
            .options(selectinload(Quote.items))
        )
        return result.scalar_one_or_none()
    
    async def get_by_number(self, quote_number: str) -> Optional[Quote]:
        """Obtiene una cotización por número"""
        result = await self.db.execute(
            select(Quote)
            .where(Quote.quote_number == quote_number)
            .options(selectinload(Quote.user))
            .options(selectinload(Quote.prospect))
            .options(selectinload(Quote.client))
            .options(selectinload(Quote.items))
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        prospect_id: Optional[int] = None,
        client_id: Optional[int] = None,
        user_id: Optional[int] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Tuple[List[Quote], int]:
        """Obtiene todas las cotizaciones con filtros"""
        query = select(Quote).options(
            selectinload(Quote.user),
            selectinload(Quote.prospect),
            selectinload(Quote.client),
            selectinload(Quote.items)
        )
        
        # Filtros
        filters = []
        
        if prospect_id:
            filters.append(Quote.prospect_id == prospect_id)
        
        if client_id:
            filters.append(Quote.client_id == client_id)
        
        if user_id:
            filters.append(Quote.user_id == user_id)
        
        if status:
            filters.append(Quote.status == status)
        
        if search:
            search_term = f"%{search}%"
            filters.append(
                or_(
                    Quote.quote_number.ilike(search_term),
                    Quote.title.ilike(search_term)
                )
            )
        
        if start_date:
            filters.append(Quote.created_at >= start_date)
        
        if end_date:
            filters.append(Quote.created_at <= end_date)
        
        if filters:
            query = query.where(and_(*filters))
        
        # Contar total
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.execute(count_query)
        total_count = total.scalar()
        
        # Paginación y orden
        query = query.order_by(Quote.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        
        return result.scalars().all(), total_count
    
    async def update(self, quote_id: int, update_data: dict) -> Optional[Quote]:
        """Actualiza una cotización"""
        quote = await self.get_by_id(quote_id)
        if not quote:
            return None
        
        for key, value in update_data.items():
            if value is not None and hasattr(quote, key):
                setattr(quote, key, value)
        
        # Recalcular totales si cambió algún item
        await self._recalculate_totals(quote)
        
        await self.db.commit()
        await self.db.refresh(quote)
        return quote
    
    async def delete(self, quote_id: int) -> bool:
        """Elimina una cotización"""
        quote = await self.get_by_id(quote_id)
        if not quote:
            return False
        
        await self.db.delete(quote)
        await self.db.commit()
        return True
    
    async def update_item(self, item_id: int, update_data: dict) -> Optional[QuoteItem]:
        """Actualiza un item de cotización"""
        result = await self.db.execute(
            select(QuoteItem).where(QuoteItem.id == item_id)
        )
        item = result.scalar_one_or_none()
        if not item:
            return None
        
        for key, value in update_data.items():
            if value is not None and hasattr(item, key):
                setattr(item, key, value)
        
        await self.db.commit()
        await self.db.refresh(item)
        
        # Recalcular totales de la cotización
        quote = await self.get_by_id(item.quote_id)
        if quote:
            await self._recalculate_totals(quote)
            await self.db.commit()
        
        return item
    
    async def add_item(self, quote_id: int, item_data: dict) -> Optional[QuoteItem]:
        """Agrega un item a una cotización"""
        quote = await self.get_by_id(quote_id)
        if not quote:
            return None
        
        item = QuoteItem(quote_id=quote_id, **item_data)
        self.db.add(item)
        
        await self._recalculate_totals(quote)
        await self.db.commit()
        await self.db.refresh(item)
        return item
    
    async def remove_item(self, item_id: int) -> bool:
        """Elimina un item de cotización"""
        result = await self.db.execute(
            select(QuoteItem).where(QuoteItem.id == item_id)
        )
        item = result.scalar_one_or_none()
        if not item:
            return False
        
        quote_id = item.quote_id
        
        await self.db.delete(item)
        
        # Recalcular totales de la cotización
        quote = await self.get_by_id(quote_id)
        if quote:
            await self._recalculate_totals(quote)
        
        await self.db.commit()
        return True
    
    async def _recalculate_totals(self, quote: Quote):
        """Recalcula los totales de una cotización"""
        # Cargar items si no están cargados
        if not hasattr(quote, 'items') or not quote.items:
            result = await self.db.execute(
                select(QuoteItem).where(QuoteItem.quote_id == quote.id)
            )
            quote.items = result.scalars().all()
        
        # Calcular subtotal
        subtotal = 0.0
        for item in quote.items:
            # Calcular total del item
            item.total = (item.quantity * item.unit_price) - item.discount
            if item.total < 0:
                item.total = 0
            subtotal += item.total
        
        quote.subtotal = subtotal
        quote.total = subtotal + quote.tax - quote.discount
        if quote.total < 0:
            quote.total = 0
    
    async def get_stats(self, user_id: Optional[int] = None) -> dict:
        """Obtiene estadísticas de cotizaciones"""
        query = select(Quote)
        
        if user_id:
            query = query.where(Quote.user_id == user_id)
        
        # Total de cotizaciones
        total_result = await self.db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = total_result.scalar()
        
        # Por status
        status_query = select(Quote.status, func.count()).group_by(Quote.status)
        if user_id:
            status_query = status_query.where(Quote.user_id == user_id)
        status_result = await self.db.execute(status_query)
        by_status = {status: count for status, count in status_result.all()}
        
        # Total en cotizaciones (suma de totales)
        total_value_query = select(func.sum(Quote.total))
        if user_id:
            total_value_query = total_value_query.where(Quote.user_id == user_id)
        total_value_result = await self.db.execute(total_value_query)
        total_value = total_value_result.scalar() or 0.0
        
        # Cotizaciones aceptadas (suma)
        accepted_value_query = select(func.sum(Quote.total)).where(Quote.status == 'accepted')
        if user_id:
            accepted_value_query = accepted_value_query.where(Quote.user_id == user_id)
        accepted_value_result = await self.db.execute(accepted_value_query)
        accepted_value = accepted_value_result.scalar() or 0.0
        
        return {
            "total": total,
            "by_status": by_status,
            "total_value": float(total_value),
            "accepted_value": float(accepted_value)
        }