from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import Optional, List, Tuple

from app.models.client import Client
from app.models.prospect import Prospect



class ClientRepository:

    def __init__(self, db: AsyncSession):
        self.db = db


    async def create(self, client_data:dict) -> Client:
        """ Crea un nuevo cliente """
        client = Client(**client_data)
        self.db.add(client)
        await self.db.commit()
        await self.db.refresh(client)
        return client

    async def get_by_id(self, client_id:int) -> Optional[Client]:
        """ Obtiene un cliente por id """

        result = await self.db.execute(
            select(Client)
            .where(Client.id == client_id)
            .options(selectinload(Client.created_by))
            .options(selectinload(Client.original_prospect))
        )
        return result.scalar_one_or_none()

    async def get_all(
            self,
            skip: int=0,
            limit: int=100,
            status: Optional[str] = None,
            search: Optional[str] = None,
            type: Optional[str] = None
    ) -> Tuple[List[Client], int]:
        """ Obtiene todos los clientes con filtros """

        query = select(Client).options(selectinload(Client.created_by))

        if status:
            query = query.where(Client.status == status)

        if type:
            query = query.where(Client.type == type)

        if search:
            search_term = f"%{search}%"
            query = query.where(
                (Client.company_name.ilike(search_term)) |
                (Client.company_name.ilike(search_term)) |
                (Client.email.ilike(search_term))
            )

        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.execute(count_query)
        total_count= total.scalar()

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)

        return result.scalar().all(), total_count

    async def update(self, client_id: int, update_data: dict) -> Optional[Client]:
        """ Actualiza un cliente existente """

        client = await self.get_by_id(client_id)
        if not client:
            return None

        for key, value in update_data.items():
            if value is not None and hasattr(client, key):
                setattr(client, key, value)

        await self.db.commit()
        await self.db.refresh(client)
        return client

    async def delete(self, client_id:int) -> bool:
        """ Elimina un cliente (hard delete) """

        client = await self.get_by_id(client_id)
        if not client:
            return False

        await self.db.delete(client)
        await self.db.commit()
        return True

    async def get_stats(self) -> dict:
        """ Ontiene estadísticas de clientes """

        # Total de clientes
        total_result = await self.db.execute(select(func.count()).select_from(Client))
        total = total_result.scalar()

        # Por status
        status_result = await self.db.execute(
            select(Client.status, func.count())
            .group_by(Client.status)
        )
        by_status = {status: count for status, count in status_result.all}

        # Por tipo
        type_result = await self.db.execute(
            select(Client.type, func.count())
            .group_by(Client.type)
        )
        by_type = {type: count for type, count in type_result.all()}

        return {
            "total": total,
            "by_status": by_status,
            "by_type": by_type
        }


    async def  convert_from_prospect(self, prospect_id: int, client_data:dict) -> Optional[Client]:
        """ Convierte un prospecto en cliente y actualiza su status """

        # Verificar que el prospecto existe
        result = await self.db.execute(
            select(Prospect).where(Prospect.id == prospect_id)
        )
        prospect = result.scalar_one_or_none()

        if not prospect:
            return None

        # Crear un cliente con datos del prospecto + datos adicionales
        client_dict = {
            "company_name": client_data.get("company_name") or prospect.company_name,
            "contact_name": client_data.get("contact_name") or prospect.contact_name,
            "email": client_data.get("email") or prospect.email, 
            "phone": client_data.get("phone") or prospect.phone,
            "website": prospect.website,
            "type": client_data.get("type", "company"),
            "status": "active",
            "notes": client_data.get("notes") or prospect.notes,
            "original_prospect_id": prospect_id,
            "created_by": prospect.created_by_id
        }

        # Crear el cliente
        client = Client(**client_dict)
        self.db.add(client)

        # Actualizar el prospecto a "converted"
        prospect.status = "converted"

        await self.db.commit()
        await self.db.refresh(client)

        return client