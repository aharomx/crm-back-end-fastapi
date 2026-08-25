# app/schemas/prospect.py
# app/schemas/prospect.py
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional

# Definir tipos como strings literales para Swagger
class ProspectBase(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=255)
    contact_name: str = Field(..., min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    website: Optional[str] = Field(None, max_length=255)
    status: str = Field(default="new", pattern="^(new|contacted|qualified|lost|converted)$")
    source: str = Field(default="other", pattern="^(web|referral|cold_call|social_media|event|other)$")
    notes: Optional[str] = None
    estimated_value: Optional[float] = Field(None, ge=0)

class ProspectCreate(ProspectBase):
    pass

class ProspectUpdate(BaseModel):
    company_name: Optional[str] = Field(None, min_length=1, max_length=255)
    contact_name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    website: Optional[str] = Field(None, max_length=255)
    status: Optional[str] = Field(None, pattern="^(new|contacted|qualified|lost|converted)$")
    source: Optional[str] = Field(None, pattern="^(web|referral|cold_call|social_media|event|other)$")
    notes: Optional[str] = None
    estimated_value: Optional[float] = Field(None, ge=0)

class ProspectResponse(ProspectBase):
    id: int
    created_by_id: int
    created_at: datetime
    updated_at: datetime
    created_by_email: Optional[str] = None
    created_by_username: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)