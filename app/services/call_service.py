from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Tuple
from datetime import datetime
from app.repositories.call_repository import CallRepository
from app.schemas.call import CallCreate, CallUpdate
from app.models.call import Call

class CallService:
    def __init__(self, db:AsyncSession):
        self.db = db
        self.repository = CallRepository(db)

    async def create_call(
            self, 
            call_data: CallCreate,
            user_id: int
    ) -> Call:
        """ Crea un nuevo registro de llamada """

        # Validar que al menos un contacto (prospecto o cliente) este presente

        if not call_data.prospect_id and not call_data.client.id:
            raise ValueError("Either prospect_id or client_id mus be provided")

        data_dict = call_data.model_dump()
        data_dict["user_id"] = user_id
        return await self.repository.create(data_dict)

    async def get_call(self, call_id:int) -> Optional[Call]:
        """ Obtiene un allamada por ID """

        return await self.repository.get_by_id(call_id)


    async def get_calls(
            self,
            skip: int = 0,
            limit: int = 0,
            prospect_id: Optional[int] = None,
            client_id: Optional[int] = None,
            user_id: Optional[int] = None,
            status: Optional[str] = None,
            type: Optional[str] = None,
            start_date: Optional[datetime] = None,
            end_date: Optional[datetime] = None,
            search: Optional[str] = None,
    ) -> Tuple[List[Call], int]:
        """ Obtiene lista de llamadas con filtros """

        return await self.repository.get_all(
            skip, limit, prospect_id, client_id, user_id, 
            status, type, start_date, end_date, search
        )


    async def get_calls_by_prospect(self, prospect_id: int) -> List[Call]:
        """ Obtiene todas las llamadas de un prospecto """

        return await self.repository.get_by_prospect(prospect_id) 

    async def get_call_by_client(self, client_id: int) -> List[Call]:
        """ Obtiene todas las llamadas de un cliente """

        return await self.repository.get_by_client(client_id)

    async def update_call(
            self,
            call_id: int,
            update_data: CallUpdate,
    ) -> Optional[Call]:
        """ Actualiza una llamada """

        update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}

        if not update_dict:
            return await self.repository.get_by_id(call_id)

        return await self.repository.update(call_id, update_dict)

    async def delete_call(self, call_id:int) -> bool:
        """ Elimina una llamada """

        return await self.repository.delete(call_id)


    async def get_stats(self, user_id: Optional[int] = None) -> dict:
        """ Obtiene las estadísticas de llamadas """

        return await self.repository.get_stats(user_id)

    


