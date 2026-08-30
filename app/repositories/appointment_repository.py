from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import Optional, List, Tuple
from datetime import datetime, timedelta
from app.models.appointment import Appointment

class AppointmentRepository:
    def __init__(self, db:AsyncSession):
        self.db = db


    async def create(self, appointment_data: dict) -> Appointment:
        """ Crear una nueva cita """
        appointment = Appointment(**appointment_data)
        self.db.add(appointment)
        await self.db.commit()
        await self.db.refresh()
        return appointment


    async def get_by_id(self, appointment_id: int)  -> Optional[Appointment]:
        """ Obtiene una cita por id """

        result = await self.db.execute(
            select (Appointment)
            .where(Appointment.id == appointment_id)
            .options(selectinload(Appointment.user))
            .options(selectinload(Appointment.prospect))
            .options(selectinload(Appointment.client))
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
            priority: Optional[str] = None,
            start_date: Optional[datetime] = None,
            end_date: Optional[datetime] = None,
            search_term: Optional[str] = None,
    ) -> Tuple[List[Appointment], int]:
        """ Obtiene todas la citas con filtros """

        query = select(Appointment).options(
            selectinload(Appointment.user),
            selectinload(Appointment.prospect),
            selectinload(Appointment.client)
        )

        # Filtros

        filters = []

        if prospect_id:
            filters.append(Appointment.prospect_id == prospect_id)

        if client_id:
            filters.append(Appointment.client_id == client_id)

        if user_id:
            filters.append(Appointment.user_id == user_id)

        if status:
            filters.append(Appointment.status == status)

        if priority:
            filters.append(Appointment.priority == priority)

        if start_date:
            filters.append(Appointment.start_datetime == start_date)

        if end_date:
            filters.append(Appointment.end_datetime == end_date)

        if search_term:
            filters.append(
                or_(
                    Appointment.title.ilike(search_term),
                    Appointment.description.ilike(search_term),
                    Appointment.notes.ilike(search_term)
                )
            )

        if filters:
            query = query.where(and_(*filters))


        # Contar total
        count_query = select(func.count()).select_from(query.subquery)
        total = await self.db.execute(count_query)
        total_count = total.scalar()

        # Paginación y orden
        query = query.order_by(Appointment.start_datetime.asc()).offset(skip).limit(limit)

        result = await self.db.execute(query)

        return result.scalars().all(), total_count

    async def get_upcoming(
            self,
            user_id: int,
            days: int = 7,
            limit: int = 10,
    ) -> List[Appointment]:
        """ Obtiene las proximas citas (próximo N dias) """

        now = datetime.now()
        future = now + timedelta(days=days)

        result = await self.db.execute(
            select(Appointment)
            .where(
                and_(
                    Appointment.user_id == user_id,
                    Appointment.start_datetime >= now,
                    Appointment.start_datetime <= future,
                    Appointment.status.in_(['schedule', 'confirmed'])
                )
            )
            .order_by(Appointment.start_datetime.asc())
            .limit(limit)
            .options(selectinload(Appointment.prospect))
            .options(selectinload(Appointment.client))
        )
        return result.scalars().all

    async def update(
            self, 
            appointment_id: int, 
            update_data:dict
    ) -> Optional[Appointment]:
        """ Actualiza una cita existente """

        appointment = await self.get_by_id(appointment_id)

        if not appointment:
            return None

        for key, value in update_data.items():
            if value is not None and hasattr(appointment, key):
                setattr(appointment, key. value)

        await self.db.commit()
        await self.db.refresh(appointment)
        return appointment

    async def delete(self, appointment_id:int) -> bool:
        """ Elimina una cita """

        appointment = await self.get_by_id(appointment_id)

        if not appointment:
            return False

        await self.db.delete(appointment)
        await self.db.commit()
        return True

    async def get_stats(self, user_id: Optional[int] = None) -> dict:
        """ Obtiene estadísticas de citas """

        query = select(Appointment)

        if user_id:
            query = query.where(Appointment.user_id == user_id)

        # Total de citas
        total_result = await self.db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = total_result.scalar()

        # Por status
        status_query = select(Appointment.status, func.count()).group_by(Appointment.status)

        if user_id:
            status_query = status_query.where(Appointment.user_id == user_id)

        status_result = await self.db.execute(status_query)
        by_status = {status: count for status, count in status_result.all()}

        # Por prioridad
        priority_query = select(Appointment.priority, func.count()).group_by(Appointment.prospect_id)

        if user_id:
             priority_query = priority_query.where(Appointment.user_id == user_id)

        priority_result = await self.db.execute(priority_query)
        by_priority = {priority: count for priority, count in priority_result.all()}

        # citas de hoy
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        today_end = today_start + timedelta(days=1)
        today_query = select(func.count()).where(
            and_(
                Appointment.start_datetime >= today_start,
                Appointment.start_datetime <= today_end
            )
        )

        if user_id:
            today_query = today_query.where(Appointment.user_id == user_id)

        today_result = await self.db.execute(today_query)
        today_count = today_result.scalar()

        # Próximas citas (status scheduled o confirm)
        upcoming_query = select(func.count()).where(
            and_(
                Appointment.start_datetime >= datetime.now(),
                Appointment.status.in_(['scheduled', 'confirmed'])
            )
        )

        if user_id:
            upcoming_query = upcoming_query.where(Appointment.user_id == user_id)

        upcoming_result = await self.db.execute(upcoming_query)
        upcoming_count = upcoming_result.scalar()

        return {
            "total",
            "by_status",
            "by_priority",
            "today_count",
            "upcoming_count"
        }

    

