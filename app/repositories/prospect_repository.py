# app/repositories/prospect_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import Optional, List, Tuple
from app.models.prospect import Prospect

class ProspectRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, prospect_data: dict) -> Prospect:
        prospect = Prospect(**prospect_data)
        self.db.add(prospect)
        await self.db.commit()
        await self.db.refresh(prospect)
        return prospect
    
    async def get_by_id(self, prospect_id: int) -> Optional[Prospect]:
        result = await self.db.execute(
            select(Prospect)
            .where(Prospect.id == prospect_id)
            .options(selectinload(Prospect.created_by))
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Prospect], int]:
        query = select(Prospect).options(selectinload(Prospect.created_by))
        
        if status:
            query = query.where(Prospect.status == status)
        
        if search:
            search_term = f"%{search}%"
            query = query.where(
                (Prospect.company_name.ilike(search_term)) |
                (Prospect.contact_name.ilike(search_term)) |
                (Prospect.email.ilike(search_term))
            )
        
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.execute(count_query)
        total_count = total.scalar()
        
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        
        return result.scalars().all(), total_count
    
    async def update(self, prospect_id: int, update_data: dict) -> Optional[Prospect]:
        prospect = await self.get_by_id(prospect_id)
        if not prospect:
            return None
        
        for key, value in update_data.items():
            if value is not None and hasattr(prospect, key):
                setattr(prospect, key, value)
        
        await self.db.commit()
        await self.db.refresh(prospect)
        return prospect
    
    async def delete(self, prospect_id: int) -> bool:
        prospect = await self.get_by_id(prospect_id)
        if not prospect:
            return False
        
        await self.db.delete(prospect)
        await self.db.commit()
        return True
    
    async def get_stats(self) -> dict:
        total_result = await self.db.execute(select(func.count()).select_from(Prospect))
        total = total_result.scalar()
        
        status_result = await self.db.execute(
            select(Prospect.status, func.count())
            .group_by(Prospect.status)
        )
        by_status = {status: count for status, count in status_result.all()}
        
        value_result = await self.db.execute(
            select(func.sum(Prospect.estimated_value))
            .where(Prospect.estimated_value.isnot(None))
        )
        total_value = value_result.scalar() or 0.0
        
        return {
            "total": total,
            "by_status": by_status,
            "total_estimated_value": float(total_value)
        }