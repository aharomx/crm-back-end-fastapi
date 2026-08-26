from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional

# Base para ceación/actualización
class ClientBase(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=255)
    contact_name: str = Field(..., min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    website: Optional[str] = Field(None, max_length=255)

    # Tipos u status con validación
    type: str = Field(default="company", pattern="^(company|individual)$")
    status: str = Field(default="active", pattern="^(active|inactive|archived)$")
    industry: Optional[str] = Field(None, max_length=100)

    # Dirección
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)

    notes: Optional[str] = None
    original_prospect_id: Optional[int] = None

# Para crear un nuevo cliente
class ClientCreate(ClientBase):
    pass

# Para actualizar un cliente todos los campos son opcionales
class ClientUpdate(BaseModel):
    company_name: Optional[str] = Field(..., min_length=1, max_length=255)
    contact_name: Optional[str] = Field(..., min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    website: Optional[str] = Field(None, max_length=255)

    # Tipos u status con validación
    type: Optional[str] = Field(default="company", pattern="^(company|individual)$")
    status: Optional[str] = Field(default="active", pattern="^(active|inactive|archived)$")
    industry: Optional[str] = Field(None, max_length=100)

    # Dirección
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)

    notes: Optional[str] = None
    original_prospect_id: Optional[int] = None

# Para responder (incluye información del creador y prospecto original)
class ClientResponse(ClientBase):
    id: int
    created_at: datetime
    updated_at: datetime

    # Información del creador
    created_by_email: Optional[str] = None
    created_by_username: Optional[str] = None

    # Información del prospecto original (opcional)
    original_prospect_company: Optional[str] = None
    original_prospect_contact: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# Para convertir un prospecto en cliente
class ConvertProspectToClient(BaseModel):
    prospect_id: int
    # Si quieres sobreescribir algún campo del prospecto
    company_name: Optional[str] = None
    contact_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    types: str = Field(default="company", pattern="^(company|individual)$")
    notes: Optional[str] = None
