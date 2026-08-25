# app/api/v1/prospects.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.core.dependencies import get_current_user, verify_ownership
from app.models.user import User
from app.schemas.prospect import (
    ProspectCreate, 
    ProspectUpdate, 
    ProspectResponse
)
from app.services.prospect_service import ProspectService

router = APIRouter(prefix="/prospects", tags=["Prospects"])

@router.post("/", response_model=ProspectResponse, status_code=status.HTTP_201_CREATED)
async def create_prospect(
    prospect_data: ProspectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ProspectService(db)
    prospect = await service.create_prospect(prospect_data, current_user.id)
    
    response = ProspectResponse.model_validate(prospect)
    response.created_by_email = prospect.created_by.email
    response.created_by_username = prospect.created_by.username
    
    return response

@router.get("/", response_model=List[ProspectResponse])
async def get_prospects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None, pattern="^(new|contacted|qualified|lost|converted)$"),
    search: Optional[str] = Query(None, min_length=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ProspectService(db)
    prospects, total = await service.get_prospects(skip, limit, status, search)
    
    response = []
    for prospect in prospects:
        prospect_response = ProspectResponse.model_validate(prospect)
        prospect_response.created_by_email = prospect.created_by.email
        prospect_response.created_by_username = prospect.created_by.username
        response.append(prospect_response)
    
    return response

@router.get("/{prospect_id}", response_model=ProspectResponse)
async def get_prospect(
    prospect_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ProspectService(db)
    prospect = await service.get_prospect(prospect_id)
    
    if not prospect:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prospect not found"
        )
    
    await verify_ownership(prospect.created_by_id, current_user)
    
    response = ProspectResponse.model_validate(prospect)
    response.created_by_email = prospect.created_by.email
    response.created_by_username = prospect.created_by.username
    
    return response

@router.put("/{prospect_id}", response_model=ProspectResponse)
async def update_prospect(
    prospect_id: int,
    update_data: ProspectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ProspectService(db)
    
    existing = await service.get_prospect(prospect_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prospect not found"
        )
    
    await verify_ownership(existing.created_by_id, current_user)
    
    prospect = await service.update_prospect(prospect_id, update_data)
    
    response = ProspectResponse.model_validate(prospect)
    response.created_by_email = prospect.created_by.email
    response.created_by_username = prospect.created_by.username
    
    return response

@router.delete("/{prospect_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prospect(
    prospect_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ProspectService(db)
    
    existing = await service.get_prospect(prospect_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prospect not found"
        )
    
    await verify_ownership(existing.created_by_id, current_user)
    
    deleted = await service.delete_prospect(prospect_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete prospect"
        )
    
    return None

@router.get("/stats/dashboard", response_model=dict)
async def get_prospect_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ProspectService(db)
    stats = await service.get_stats()
    return stats