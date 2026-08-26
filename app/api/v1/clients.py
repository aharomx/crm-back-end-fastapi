from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.core.dependencies import get_current_user, verify_ownership
from app.models.user import User
from app.schemas.client import (
    ClientCreate,
    ClientUpdate,
    ClientResponse,
    ConvertProspectToClient
)
from app.services.client_service import ClientService

router = APIRouter(prefix="/clients", tags=["Clients"])

@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    client_data: ClientCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crea un nuevo cliente"""
    service = ClientService(db)
    client = await service.create_client(client_data, current_user.id)
    
    response = ClientResponse.model_validate(client)
    response.created_by_email = client.created_by.email
    response.created_by_username = client.created_by.username
    
    return response

@router.post("/convert-from-prospect", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def convert_prospect_to_client(
    conversion_data: ConvertProspectToClient,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Convierte un prospecto en cliente.
    - Actualiza el prospecto a 'converted'
    - Crea un nuevo cliente con los datos del prospecto
    - Mantiene la relación entre ambos
    """
    service = ClientService(db)
    client = await service.convert_prospect_to_client(conversion_data, current_user.id)
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prospect not found"
        )
    
    response = ClientResponse.model_validate(client)
    response.created_by_email = client.created_by.email
    response.created_by_username = client.created_by.username
    
    if client.original_prospect:
        response.original_prospect_company = client.original_prospect.company_name
        response.original_prospect_contact = client.original_prospect.contact_name
    
    return response

@router.get("/", response_model=List[ClientResponse])
async def get_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None, pattern="^(active|inactive|archived)$"),
    type: Optional[str] = Query(None, pattern="^(company|individual)$"),
    search: Optional[str] = Query(None, min_length=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lista todos los clientes con filtros"""
    service = ClientService(db)
    clients, total = await service.get_clients(skip, limit, status, search, type)
    
    response = []
    for client in clients:
        client_response = ClientResponse.model_validate(client)
        client_response.created_by_email = client.created_by.email
        client_response.created_by_username = client.created_by.username
        
        if client.original_prospect:
            client_response.original_prospect_company = client.original_prospect.company_name
            client_response.original_prospect_contact = client.original_prospect.contact_name
        
        response.append(client_response)
    
    return response

@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene un cliente específico"""
    service = ClientService(db)
    client = await service.get_client(client_id)
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    await verify_ownership(client.created_by_id, current_user)
    
    response = ClientResponse.model_validate(client)
    response.created_by_email = client.created_by.email
    response.created_by_username = client.created_by.username
    
    if client.original_prospect:
        response.original_prospect_company = client.original_prospect.company_name
        response.original_prospect_contact = client.original_prospect.contact_name
    
    return response

@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: int,
    update_data: ClientUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualiza un cliente existente"""
    service = ClientService(db)
    
    existing = await service.get_client(client_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    await verify_ownership(existing.created_by_id, current_user)
    
    client = await service.update_client(client_id, update_data)
    
    response = ClientResponse.model_validate(client)
    response.created_by_email = client.created_by.email
    response.created_by_username = client.created_by.username
    
    if client.original_prospect:
        response.original_prospect_company = client.original_prospect.company_name
        response.original_prospect_contact = client.original_prospect.contact_name
    
    return response

@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Elimina un cliente"""
    service = ClientService(db)
    
    existing = await service.get_client(client_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    await verify_ownership(existing.created_by_id, current_user)
    
    deleted = await service.delete_client(client_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete client"
        )
    
    return None

@router.get("/stats/dashboard", response_model=dict)
async def get_client_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene estadísticas de clientes"""
    service = ClientService(db)
    stats = await service.get_stats()
    return stats