from pydantic import BaseModel, Field, ConfigDict, validator
from datetime import datetime
from typing import Optional


# Base para la creación/actualización
class AppointmentBase(BaseModel):
    prospect_id: Optional[int] = None
    client_id: Optional[int] = None
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    start_datetime: datetime
    end_datetime: datetime
    location: str = Field(default="online", pattern="^(online|office|client_site|phone)$")
    meeting_link: Optional[str] = Field(None, max_length=500)
    status: str = Field(default="scheduled", pattern="^(scheduled|confirmed|completed|cancelled|rescheduled)$")
    priority: str = Field(default="medium", pattern="^(low|medium|high)$")
    reminder_minutes: int = Field(default=15, ge=0, le=1440) # 0 a 24 hrs
    notes: Optional[str] = None

    
    @validator('end_datetime')
    def validate_end_datetime(cls, v, values):
        """ Asegura que la fecha de fin sea posterior a la de inicio """

        if 'start_datetime' in values and v <= values['start_datetime']:
            raise ValueError('End datetime must be after start datetime')
        return v

    @validator('start_datetime')
    def validate_start_datetime(cls, v, values):
        """ Asegura que la fecha de inicio no sea en el pasado """

        if v < datetime.now():
            raise ValueError('Start datetime cannot be in the past')

        return v

    # Para crear una nueva cita
class AppointmentCreate(AppointmentBase):
    pass

# Para actualizar una cita (Todos los campos opcionales) 
class AppointmentUpdate(BaseModel):
    prospect_id: Optional[int] = None
    client_id: Optional[int] = None
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    location: Optional[str] = Field(None, pattern="^(online|office|client_site|phone)$")
    meeting_link: Optional[str] = Field(None, pattern="^(scheduled|confirmed|completed|cancelled|rescheduled)$")
    priority: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    reminder_minutes: Optional[int] = Field(None, ge=0, le=1440)
    note: Optional[str] = None


# Para responder
class AppointmentResponse(AppointmentBase):
    id: int
    user_id: int
    reminder_sent: bool
    create_at: datetime
    update_at: datetime

    # Información del usuario
    user_email: Optional[str] = None
    user_username: Optional[str] = None

    # Información del prospecto (si existe)
    prospect_company: Optional[str] = None
    prospect_contact: Optional[str] = None

    # Información del cliente (si existe)
    client_company: Optional[str] = None
    client_contact: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)



    
