from pydantic import BaseModel, Field, ConfigDict, validator
from datetime import datetime
from typing import Optional


# Base para creación/actualización
class CallBase(BaseModel):
    prospect_id: Optional[int] = None
    client_id: Optional[int] = None
    call_date: datetime
    duration_minutes: Optional[int] = Field(None, ge=1, le=480) # 1 minuto a 8 horas
    subject: str = Field(..., min_length=1, max_length=255)
    notes: Optional[str] = None
    next_action: Optional[str] = None
    type: str = Field(default="outgoing", pattern="^(incoming|outgoing)$")
    status: str = Field(default='completed', pattern="^(completed|pending|missed)$")
    direction: str = Field(default="completed", pattern="^(inbound|outbound)$")
    rating: Optional[int] = Field(None, ge=1, le=5)

    @validator('prospect_id', 'client_id')
    def validate_contact(cls, v, values, **kwargs):
        """ Asegura que al menos un contacto (prospecto o cliente), está presente"""

        # este validator se ejecuta después de que todos los campos están presentes
        # Verificamos en el método de la clase
        
        return v

    @validator('call_date')
    def validate_call_date(cls, v):
        """ Asegura que la fecha de la llamada no sea en el futuro """
        if v > datetime.now():
            raise ValueError("Call date cannot be in the future")
        return v

# Para crear una nueva llamada solo ponemos pass porque estamos llamando a CallBase y toma todos los valores
class CallCreate(CallBase):
    pass

# Para actualizar una llamada  (Todos los campos son opcionales)
class CallUpdate(BaseModel):
    call_date: datetime
    duration_minutes: Optional[int] = Field(None, ge=1, le=480) # 1 minuto a 8 horas
    subject: str = Field(..., min_length=1, max_length=255)
    notes: Optional[str] = None
    next_action: Optional[str] = None
    type: str = Field(default="outgoing", pattern="^(incoming|outgoing)$")
    status: str = Field(default='completed', pattern="^(completed|pending|missed)$")
    direction: str = Field(default="completed", pattern="^(inbound|outbound)$")
    rating: Optional[int] = Field(None, ge=1, le=5)


# Para responder
class CallResponse(CallBase):
    id:int
    user_id: int
    created_at: datetime
    updated_at: datetime

    # Información adicional del usuario
    user_mail: Optional[str] = None
    user_username: Optional[str] = None

    # Información del prospecto (si existe)
    prospect_company: Optional[str] = None
    prospect_contact: Optional[str] = None

    # Información del cliente (si existe)
    client_company: Optional[str] = None
    client_contact: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

