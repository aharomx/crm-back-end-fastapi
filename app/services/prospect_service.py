from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Tuple
from app.repositories.prospect_repository import ProspectRepository
from app.schemas.prospect import ProspectCreate, ProspectUpdate
from app.models.prospect import Prospect


class ProspectService:
    """ Servicio para la logica del negocio de prospectos """

    def __init__(self, db:AsyncSession):
        self.db = db
        self.repository = ProspectRepository(db)


    async def create_prospect(
            self,
            prospect_data: ProspectCreate,
            user_id: int
    ) -> Prospect:
        """ Crea un nuevo prospecto asociado al usuario actual """

        # Convertir Pydantic a dict y agregar created_by_id
        data_dict = prospect_data.model_dump()
        data_dict["created_by_id"] = user_id

        return await self.repository.create(data_dict)

    async def get_prospect(self, prospect_id: int) -> Optional[Prospect]:
        """ Obtiene prospecto por id """
        return await self.repository.get_by_id(prospect_id)

    async def get_prospects(
            self,
            skip: int = 0,
            limit: int = 100,
            status: Optional[str] = None,
            search: Optional[str] = None
    ) -> Tuple[List[Prospect], int]:
        """ Obtiene lista de prospectos con filtros """

        return await self.repository.get_all(skip, limit, status, search)

    async def update_prospects(
            self,
            prospect_id: int,
            update_data: ProspectUpdate
    ) -> Optional[Prospect]:
        """ Actualiza un prospecto """

        # Filtrar campos None
        update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None} 

        if not update_dict:
            return await self.repository.get_by_id(prospect_id)

        return await self.repository.update(prospect_id, update_dict)

    async def delete_prospect(self, prospect_id: int) -> bool:
        """ Elimina un prospecto """

        return await self.repository.delete(prospect_id)

    async def get_stats(self) -> dict:
        """ Obtiene las estadísticas de prospectos """

        return await self.repository.get_stats()
