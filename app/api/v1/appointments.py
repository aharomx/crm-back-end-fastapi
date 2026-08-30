from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.core.dependencies import get_current_user, verify_ownership
from app.models.user import User
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse
)
from app.services.appointment_service import AppointmentService

router = APIRouter(prefix="/appointments", tags=["Appointments"])

@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appontment(
    appointment_data: AppointmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """ 
        Crear una nueva cita.
        Debe de estar asociada a un prospecto o cliente
    """

    service = AppointmentService(db)

    try:
        appointment =await service.create_appointment(appointment_data, current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    response = AppointmentResponse.model_validate(appointment)
    response.user_email = appointment.user.email
    response.user_username = appointment.user.username

    if appointment.prospect:
        response.prospect_company = appointment.prospect.company_name
        response.prospect_contact = appointment.prospect.contact_name

    if appointment.client:
        response.client_company = appointment.client.company_name
        response.client_contact = appointment.client.contact_name

    return response

@router.get("/", response_model=List[AppointmentResponse])
async def get_appointments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    prospect_id: Optional[int] = None,
    client_id: Optional[int] = None,
    status: Optional[str] = Query(None, patternL= "^(scheduled|confirmed|completed|cancelled|rescheduled)$"),
    priority: Optional[str] = Query(None, pattern="^(low|medium|high)$"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    search: Optional[str] =Query(None, min_length=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """ Lista todas las citas con filtros """

    service = AppointmentService(db)

    appointments, total = await service.get_appointments(
        skip, limit, prospect_id, client_id, current_user.id,
        status, priority, start_date, end_date, search
    )

    

    response = []
    for appointment in appointments:
        appointment_response = AppointmentResponse.model_validate(appointment)
        appointment_response.user_email = appointment.user.email
        appointment_response.user_username = appointment.user.username

        if appointment.prospect:
            appointment_response.prospect_company = appointment.prospect.company_name
            appointment_response.prospect_contact = appointment.prospect.contact_name

        if appointment.client:
            appointment_response.client_company = appointment.client.company_name
            appointment_response.client_contact = appointment.client.contact_name

        response.append(appointment_response)

    return response

@router.get("/upcoming", response_model=List[AppointmentResponse])
async def get_upcoming_appointment(
    days: int = Query(7, ge=1, l=30),
    limit: int = Query(10, ge=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """ Obtiene las próximas citas (próximos N dias)"""

    service = AppointmentService(db)
    appointments = await service.get_upcoming_appointments(current_user.id, days, limit)

    response = []

    for appointment in appointments:
        appointment_response = AppointmentResponse.model_validate(appointment)
        appointment_response.user_email = appointment.user.email
        appointment_response.user_username = appointment.user.username

        if appointment.prospect:
            appointment_response.prospect_company = appointment.prospect.company_name
            appointment_response.prospect_contact = appointment.prospect.contact_name

        if appointment.client:
            appointment_response.client_company = appointment.client.company_name
            appointment_response.client_contact = appointment.client.contact_name

        response.append(appointment_response)

    return response

@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """ Obtiene una cita específica por ID"""

    service = AppointmentService(db)
    appointment = await service.get_appointment(appointment_id)

    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )

    await verify_ownership(appointment.user_id, current_user)

    response = AppointmentResponse.model_validate(appointment)
    response.user_email = appointment.user.email
    response.user_username = appointment.user.username

    if appointment.prospect:
        response.prospect_company = appointment.prospect.company_name
        response.prospect_contact = appointment.prospect.contact_name

    if appointment.client:
        response.client_company = appointment.client.company_name
        response.client_contact = appointment.client.contact_name

    return response

@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: int,
    update_data: AppointmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    service = AppointmentService(db)

    existing = await service.get_appointment(appointment_id)

    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )

    await verify_ownership(existing.user_id, current_user)

    appointment = await service.update_appointment(appointment_id, update_data)

    response = AppointmentResponse.model_validate(appointment)
    response.user_email = appointment.user.email
    response.user_username= appointment.user.username

    if appointment.prospect:
        response.prospect_company = appointment.prospect.company_name
        response.prospect_contact = appointment.prospect.contact_name

    if appointment.client:
        response.client_company = appointment.client.company_name
        response.client_contact = appointment.client.contact_name

    return response

@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_appointment(
    appointment_id: int,
    db: AsyncSession = Depends(get_current_user),
    current_user: User = Depends(get_current_user)
):
    """ Elimina una cita """

    service = AppointmentService(db)

    existing = await service.get_appointment(appointment_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )

    await verify_ownership(existing.user_id, current_user)

    deleted = await service.delete_appointment(appointment_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete appointment"
        )

    return None

@router.get("/stats/dashboard", response_model=dict)
async def get_appointment_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """ Obtiene estadísticas de vitas para el dashboard """

    service = AppointmentService(db)
    stats = await service.get_stats(current_user.id)

    return stats



