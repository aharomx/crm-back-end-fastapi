from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.core.dependencies import get_current_user, verify_ownership
from app.models.user import User
from app.schemas.call import CallCreate, CallUpdate, CallResponse
from app.services.call_service import CallService

router = APIRouter(prefix="/calls", tags=["Calls"])

@router.post("/", response_model=CallResponse, status_code=status.HTTP_201_CREATED)
async def create_call(
    call_data: CallCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """ 
    Crea un nuevo registro de llamada
    Debe de estar asociado a un prospecto o a un cliente
    """

    service = CallService(db)

    try:
        call=await service.create_call(call_data, current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)

        )

    response = CallResponse.model_validate(call)
    response.user_email = call.user.email
    response.user_username = call.user.username

    if call.prospect:
        response.prospect_company = call.prospect.company_name
        response.prospect_contact = call.prospect.contact_name

    if call.client:
        response.client_company = call.client.company_name
        response.client_contact = call.client.contact_name

    return response


@router.get("/", response_model=List[CallResponse])
async def get_calls(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    prospect_id: Optional[int] = None,
    client_id: Optional[int] = None,
    status: Optional[str] = Query(None, pattern="^(completed|pending|missed)$"),
    type: Optional[str] = Query(None, pattern="^(incoming|outgoing)$"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    search: Optional[str] = Query(None, min_length=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """ Lista todas las llamadas con filtros """

    service = CallService(db)
    calls, total = await service.get_calls(
        skip, limit, prospect_id, client_id, current_user.id,
        status, type, start_date, end_date, search
    )

    response = []
    for call in calls:
        call_response = CallResponse.model_validate(call)
        call_response.user_mail = call.user.email
        call_response.user_username = call.user_username

        if call.prospect:
            call_response.prospect_company = call.prospect.company_name
            call_response.prospect_contact = call.prospect.contact_name

        if call.client:
            call_response.client_company = call.client.company_name
            call_response.client_contact = call.client.contact_name

        response.append(call_response)

    return response


@router.get("/{call_id}", response_model=CallResponse)
async def get_call(
    call_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """ Obtiene una llamada específica por ID """

    service = CallService(db)
    call = await service.get_call(call_id)

    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Call not found"
        )

    await verify_ownership(call.user_id, current_user)

    response = CallResponse.model_validate(call)
    response.user_mail = call.user.email
    response.user_username = call.user.username

    if call.prospect:
        response.prospect_company = call.prospect.company_name
        response.prospect_contact = call.prospect.contact_name

    if call.client:
        response.client_company = call.client.company_name
        response.client_contact = call.client.contact_name

    return response


@router.put("/{call_id}", response_model=CallResponse)
async def update_call(
    call_id: int,
    update_data: CallUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """ Actualiza una llamada existente """

    service = CallService(db)

    existing = await service.get_call(call_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Call not found"
        )

    await verify_ownership(existing.user_id, current_user)

    call = await service.update_call(call_id, update_data)

    response = CallResponse.model_validate(call)
    response.user_mail = call.user.email
    response.user_username = call.user.username

    if call.prospect:
        response.prospect_company = call.prospect.company_name
        response.prospect_contact = call.prospect.contact_name


    if call.client:
        response.client_company = call.client.company_name
        response.client_contact = call.client.contact_name

    return response


@router.delete("/{call_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_call(
    call_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """ Elimina una llamada """

    service = CallService(db)

    existing = await service.get_call(call_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Call not found"
        )

    await verify_ownership(existing.user_id, current_user)

    deleted = await service.delete_call(call_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete call"
        )

    return None

@router.get("/stats/dashboard", response_model=dict)
async def get_call_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """ Obtiene estadísticas de llamadas para el dashboard"""

    service = CallService(db)
    stats = await service.get_stats(current_user.id)

    return stats

