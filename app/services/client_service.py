from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Tuple
from app.repositories.client_repository import ClientRepository
from app.schemas.client import (
    ClientCreate,
    ClientUpdate,
    ConvertProspectToClient
)
from app.models.client import Client


class ClientService:

    def __init__(self, db:AsyncSession):
        self.db = db
        self.repository = ClientRepository(db)


    async def create_client(
            self,
            client_data: ClientCreate,
            user_id: int
    ) -> Client:
        """ Crea un nuevo Cliente """
        data_dict = client_data.model_dump()
        data_dict["created_by_id"] = user_id

        return await self.repository.create(data_dict)

    async def get_client(self, client_id:int) -> Optional[Client]:
        """ Obtiene un cliente por ID """

        return await self.repository.get_by_id(client_id)

    async def get_clients(
            self,
            skip: int = 0,
            limit: int = 100,
            status: Optional[str] = None,
            search: Optional[str] = None,
            type: Optional[str] = None
    ) -> Tuple[List[Client], int]:
        """ Obtiene lista de clientes con filtros """

        return await self.repository.get_all(skip, limit, status, search, type)


    async def update_client(
            self,
            client_id: int,
            update_data: ClientUpdate
    ) -> Optional[Client]:
        """ Actualiza un cliente """

        update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}

        if not update_dict:
            return await self.repository.get_by_id(client_id)

        return await self.repository.update(client_id, update_dict)



    async def delete_client(self, client_id:int) -> bool:
        """ Elimina un cliente """

        return await self.repository.delete(client_id)


    async def get_stats(self) -> dict: 
        """ Obtiene las estadísticas del cliente """

        return await self.repository.get_stats()


    async def convert_prospects_to_client(
            self,
            conversion_data: ConvertProspectToClient,
            user_id: int
    ) -> Optional[Client]:
        """ Convierte un prospecto en un cliente"""

        # Preparar datos para la conversión
        data_dict = conversion_data.model_dump()
        data_dict["created_by_id"] = user_id
        data_dict["original_prospect_id"] = conversion_data.prospect_id

        # Crear cliente desde prospecto
        
        return await self.repository.convert_from_prospect(
            conversion_data.prospect_id,
            data_dict
        )