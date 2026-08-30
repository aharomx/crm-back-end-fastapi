from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Tuple
from datetime import datetime

from app.repositories.appointment_repository import AppointmentRepository
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate
from app.models.appointment import Appointment

class AppointmentService:
    def __init__(self, db:AsyncSession):
        self.db = db
        self.repository = AppointmentRepository(db)

    async def create_appointment(
            self,
            appointment_data: AppointmentCreate,
            user_id:int
    ) -> Appointment:
        """ Crea una nueva cita """

        # Validar que al menos un contacto (prospecto o cliente) está presente
        if not appointment_data.prospect_id and not appointment_data.client_id:
            raise ValueError("Either prospect_id or client_id must be provided")

        # Validar que los tiempos sean coherentes
        if appointment_data.end_datetime <= appointment_data.start_datetime:
            raise ValueError("End datetime must be after start datetime")

        # Validar que la cita no se en el pasado
        if appointment_data.start_datetime < datetime.now():
            raise ValueError("Cannot schedule appointment in the past")

        data_dict = appointment_data.model_dump()
        data_dict["user_id"] = user_id
        return await self. repository.create(data_dict)

    async def get_appointment(self, appointment_id:int)  -> Optional[Appointment]:
        """ Obtiene una cita por ID """

        return await self.repository.get_by_id(appointment_id)

    async def get_appointments(
            self,
            skip: int=0,
            limit: int=100,
            prospect_id: Optional[int] = None,
            client_id: Optional[int] = None,
            user_id: Optional[int] = None,
            status: Optional[str] = None,
            priority: Optional[str] = None,
            start_date: Optional[datetime] = None,
            end_date: Optional[datetime]= None,
            search: Optional[str] = None
    ):
        """ Obtiene lista de citas con filtros """

        return await self.repository.get_all(
            skip,
            limit,
            prospect_id,
            client_id,
            user_id,
            status,
            priority,
            start_date,
            end_date,
            search
        )

    async def update_appointment(
            self,
            appointment_id: int,
            update_data: AppointmentUpdate
    ) -> Optional[Appointment]:
        """ Actualiza una cita """

        update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}

        if not update_dict:
            return await self.repository.get_by_id(appointment_id)

        return await self.repository.delete(appointment_id)

    async def delete_appointment(self, appointment_id: int) -> bool:
        """ Elimina una cita """

        return await self.repository.delete(appointment_id)

    async def get_stats(self, user_id: Optional[int]=None) -> dict:
        """ Obtiene estadísticas de citas """

        return await self.repository.get_stats(user_id)

    
        
