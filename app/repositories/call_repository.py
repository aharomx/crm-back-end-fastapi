from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import Optional, List, Tuple
from datetime import datetime, timedelta

from app.models.call import Call
from app.models.prospect import Prospect
from app.models.client import Client

class CallRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, call_data: dict)  -> Call:
        """ Crea un nuevo registro de llamada """
        call = Call(**call_data)
        self.db.add(call)
        await self.db.commit()
        await self.db.refresh(call)
        return call

    async def get_by_id(self, call_id:int) -> Optional[Call]:
        """ Obtiene llamadas por ID """

        result = await self.db. execute(
            select(Call)
            .where (Call.id == call_id)
            .options(selectinload(Call.user))
            .options(selectinload(Call.prospect))
            .options(selectinload(Call.client))
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
            type: Optional[str] = None,
            start_date: Optional[datetime] = None,
            end_date: Optional[datetime] = None,
            search: Optional[str] = None
    ) -> Tuple[List[Call], int]:
        """ Obtiene todas la llamadas con filtros """

        query = selectinload(Call).options(
            selectinload(Call.user),
            selectinload(Call.prospect),
            selectinload(Call.client)
        )

        # Filtros
        filters = []

        if prospect_id:
            filters.append(Call.client_id == client_id)

        if client_id:
            filters.append(Call.client_id == client_id)

        if user_id:
            filters.append(Call.user_id == user_id)

        if status:
            filters.append(Call.status == status)

        if type:
            filters.append(Call.type == type)

        if start_date:
            filters.append(Call.call_date >= start_date)

        if end_date:
            filters.append(Call.call_date <= end_date )

        if search:
            search_term = f"%{search}%"
            filters.append(
                or_(
                    Call.subjects.ilike(search_term),
                    Call.notes.ilike(search_term),
                    Call.next_action.ilike(search_term)
                )
            )

        if filters:
            query = query.where(and_(*filters))

        # Contar total
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db. execute(count_query)
        total_count = total.scalar()

        # Paginación y orden
        query = query.order_by(Call.call_date.des()).offset(skip).limit(limit)

        result = await self.db.execute(query)

        return result.scalar().all(), total_count



    async def get_by_prospect(self, prospect_id: int) -> List[Call]:
        """Obtiene todas las llamadas de un prospecto"""
        
        result = await self.db.execute(
            select(Call)
            .where(Call.prospect_id == prospect_id)
            .order_by(Call.call_date.desc())
            .options(selectinload(Call.user))
        )
        return result.scalars().all()

    async def get_by_client(self, client_id: int) -> List[Call]:
        """ Obtiene todas las llamadas de un cliente """

        result = await self.db.execute(
            select(Call)
            .where(Call.client_id == client_id)
            .order_by(Call.call_date.desc())
            .options(selectinload(Call.user))
        )

        return result.scalars().all

    async def update(self, call_id:int, update_data: dict) -> Optional[Call]:
        """ Actualiza una llamada existente """

        call = await self.get_by_id(call_id)
        if not call:
            return None

        for key, value in update_data.items():
            if value is not None and hasattr(call, key):
                setattr(call, key, value)

        await self.db.commit()
        await self.db.refresh(all)
        return call

    async def delete(self, call_id:int) -> bool:
        """ Elimina una llamada """

        call = await self.get_by_id(call_id)
        if not call:
            return False

        await self.db.delete(call)
        await self.db.commit()
        return True



    async def get_stats(self, user_id: Optional[int] = None) -> dict:
        """ Obtiene estadísticas de llamadas """


        query = select(Call)

        if user_id:
            query = query.where(Call.user_id == user_id)

        # Total de llamadas
        total_result = await self.db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = total_result.scalar()

        # Por status
        status_query = select(Call.status, func.count()).group_by(Call.status)

        if user_id:
            status_query = status_query.where(Call.user_id == user_id)

        status_result = await self.db.execute(status_query)
        by_status = {status: count for status, count in status_result.all()}

        # Por tipo
        type_query = select(Call.type, func.count()).group_by(Call.type)
        if user_id:
            type_query = type_query.where(Call.user_id == user_id)

        type_result = await self.db.execute(type_query)
        by_type = {type: count for type, count in type_result.all()}


        # Llamadas de los últimos 7 dias
        week_ago = datetime.now() - timedelta(days=7)
        recent_query = select(func.now()).where(Call.call_date >= week_ago)
        recent_result = await self.db.execute(recent_query)
        recent_calls = recent_result.scalar()


        # DUración promedio
        avg_query = select(func.avg(Call.duration_minutes))

        if user_id:
            avg_query = avg_query.where(Call.user_id == user_id)

        avg_result = await self.db.execute(avg_query)
        avg_duration = avg_result.scalar() or 0

        return {
            "total": total,
            "by_status": by_status,
            "by_type": by_type,
            "recent_calls": recent_calls,
            "avg_duration_minutes": round(float(avg_duration),2 )
        }
    