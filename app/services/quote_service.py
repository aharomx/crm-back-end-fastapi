from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Tuple
from datetime import datetime

from app.repositories.quote_repository import QuoteRepository
from app.schemas.quote import (
    QuoteCreate,
    QuoteUpdate,
    QuoteItemCreate
)
from app.models.quote import Quote

import random
import string

class QuoteService:
    def __init__(self, db:AsyncSession):
        self.db = db
        self.repository = QuoteRepository


    async def generate_quote_number(self) -> str:
        """ Generar un número unico de cotización """


        # Formato Q-YYY-XXXXX
        year = datetime.now().year

        # Generar 5 caracteres alfanuméricos
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

        return f"Q-{year}-{random_part}"

    async def create_quote(
            self,
            quote_data: QuoteCreate,
            user_id: int
    ) -> Quote:
        """ Create una nueva cotización """

        # Validar que al menos un contacto (Prospecto o cliente) esté presente
        if not quote_data.prospect_id and not quote_data.client_id:
            raise ValueError("Either prospect_id o client_id must be provided ")

        # Validar fechas
        if quote_data.expiry_date <= quote_data.issue_date:
            raise ValueError("Expiry date must be after issue date ")

        # Preparar datos
        data_dict = quote_data.model_dump(exclude={'items'})
        data_dict["user_id"] = user_id
        data_dict["quote_number"] = await self.generate_quote_number()

        # Preparar items
        items_data = [item.model_dump() for item in quote_data.items]

        return await self.repository.create(data_dict. items_data)

    async def get_quote(self, quote_id: int) -> Optional[Quote]:
        """ Obtiene una cotización por ID """

        return await self.repository.get_by_id(quote_id)

    async def get_quote_by_number(self, quote_number: str) -> Optional[Quote]:
        """ Obtiene un cotización por número """

        return await self.repository.get_by_number(quote_number)

    async def get_quotes(
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
        """ Obtiene lista de cotizaciones con filtros """

        return await self.repository.get_all(
            skip, limit, prospect_id, client_id, user_id, status,
            search, start_date, end_date
        )

    async def update_quote(
            self,
            quote_id: int,
            update_data: QuoteUpdate
    ) -> Optional[Quote]:
        """ Actualiza una cotización """

        update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}

        if not update_dict:
            return await self.repository.get_by_id(quote_id)

        return await self.repository.update(quote_id, update_dict)

    async def delete_quote(self, quote_id: int) -> bool:
        """ Elimina una cotización """

        return await self.repository.delete(quote_id)

    async def add_item(
            self, 
            quote_id: int, 
            item_data: QuoteItemCreate
    ) -> Optional[Quote]:
        """ Agrega un item a la cotización """

        # Verificar que la cotización existe
        quote = await self.get_quote(quote_id)
        if not quote:
            return None

        await self.repository.add_item(quote_id, item_data.model_dump())

        return await self.get_quote(quote_id)

    async def update_item(
            self,
            item_id: int,
            update_data: dict
    ) -> Optional[Quote]:
        """ Actualiza un item de la cotización """

        item = await self.repository.update_item(item_id, update_data)
        if not item:
            return None

        return await self.get_quote(item.quote_id)

    async def remove_item(self, item_id: int) -> Optional[Quote]:
        """ Elimina un item de la cotización """

        # Obtener el quote_id antes de eliminar
        result = await self.db.execute(
            select(QuoteItem).where(QuoteItem.id == item_id)
        )
        item = result.scalars()
        if not item:
            return None

        quote_id = item.quote_id
        await self.repository.remove_item(item_id)
        return await self.get_quote(quote_id)


    async def get_stats(self, user_id: Optional[int] = None) -> dict:
        """ Obtiene estadísticas de cotizaciones """

        return await self.repository.get_stats(user_id)

