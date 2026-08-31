from pydantic import BaseModel, Field, ConfigDict, validator 
from datetime import datetime
from typing import Optional, List


# ---------------- Quote Item Schemas ----------------
class QuoteItemBase(BaseModel):
    description: str = Field(..., min_length=1, max_length=500)
    quantity: float = Field(default=1.0, gt=0)
    unit_price: float = Field(default=0.0, ge=0)
    discount: float = Field(default=0.0, ge=0)

class QuoteItemCreate(QuoteItemBase):
    pass

class QuoteItemUpdate(BaseModel):
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    quantity: Optional[float]  = Field(None, gt=0)
    unit_price: Optional[float] = Field(None, ge=0)
    discount: Optional[float] = Field(None, ge=0)

class QuoteItemResponse(QuoteItemBase):
    id: int
    total: float

    model_config = ConfigDict(from_attributes=True)

# ---------------- Quote Schemas --------------------
class QuoteBase(BaseModel):
    prospect_id: Optional[int] = None
    client_id: Optional[int] = None
    title: str = Field(..., min_length=1, max_length=255)
    issue_date: datetime
    expiry_date: datetime
    status: str = Field(default="draft", pattern="^(draft|sent|accepted|rejected|expired)$")
    notes: Optional[str] = None
    terms: Optional[str] = None

class QuoteCreate(QuoteBase):
    items: List[QuoteItemCreate] = Field(..., min_length=1)

    @validator('expire_date')
    def validate_expiry_date(cls, v, values):
        """ Asegura que la fecha de vencimiento sea posterior a la emisión """

        if 'issue_date' in values and v <= values['issue_date']:
            raise ValueError('Expiry date must be after issue date')

        return v


class QuoteUpdate(BaseModel):
    prospect_id: Optional[int] = None
    client_id: Optional[int] = None
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    issue_date: Optional[int] = None
    expiry_date: Optional[int] = None
    status: Optional[str] = Field(None, pattern="^(draft|sent|accepted|rejected|expired)$")
    notes: Optional[str] = None
    terms: Optional[str] = None


class QuoteResponse(QuoteBase):
    id: int
    user_id: int
    quote_number: str
    subtotal: float
    tax: float
    discount: float
    total: float
    created_at: datetime
    updated_at: datetime

    # Información del usuario
    user_email: Optional[str] = None
    user_username: Optional[str] = None

    # Información del prospecto
    prospect_company: Optional[str] = None
    prospect_contact: Optional[str] = None

    # Información del cliente
    client_company: Optional[str] = None
    client_contact: Optional[str] = None

    # Items
    items: List[QuoteItemResponse] = []

    model_config = ConfigDict(from_attributes=True)



