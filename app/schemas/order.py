from pydantic import BaseModel, Field, ConfigDict, validator
from datetime import datetime
from typing import Optional, List


# ------------- Order Item Schemas ------------------
class OrderItemBase(BaseModel):
    description: str = Field(..., min_length=1, max_length=500)
    quantity: float = Field(default=1.0, gt=0)
    unit_price: float = Field(default=0.0, ge=0)
    discount: float = Field(default=0.0, ge=0)
    quote_item_id: Optional[int] = None


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemUpdate(BaseModel):
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    quantity: Optional[float] = Field(None, gt=0)
    unit_price: Optional[float] = Field(None, ge=0)
    discount: Optional[float] = Field(None, ge=0)


class OrderItemResponse(OrderItemBase):
    id: int
    total: float 

    model_config = ConfigDict(from_attributes=True)


# --------------- Order Schemas ------------------------
class OrderBase(BaseModel):
    client_id: int
    quote_id: Optional[int] = None
    order_date: datetime
    delivery_date: Optional[datetime] = None
    status: str= Field(default="draft", pattern="^(draft|confirmed|in_progress|shipped|delivered|cancelled)$")
    priority: str = Field(default="medium", pattern="^(low|medium|high)$")
    notes: Optional[str] = None
    shipping_address: Optional[str] = None

class OrderCreate(OrderBase):
    items: List[OrderItemCreate] = Field(..., min_length=1)

    @validator('delivery_date')
    def validate_delivery_date(cls, v, values):
        """ Asegura que la fecha de entrega sea posterior a la fecha del pedido"""
        if v and 'order_date' in values and v <= values['order_date']:
            raise ValueError('Delivery date must be after order date')
        return v


class OrderCreateFromQuote(BaseModel):
    quote_id: int
    delivery_date: Optional[datetime] = None
    priority: str = Field(default="medium", pattern="^(low|medium|high)$")
    notes: Optional[str] = None
    shipping_address: Optional[str] = None


class OrderUpdate(BaseModel):
    delivery_date: Optional[datetime] = None
    status: Optional[str]= Field(None, pattern="^(draft|confirmed|in_progress|shipped|delivered|cancelled)$")
    priority: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    notes: Optional[str] = None
    shipping_address: Optional[str] = None


class OrderResponse(OrderBase):
    id: int
    user_id: int
    order_number: str
    subtotal: float
    tax: float
    discount: float 
    total: float 
    created_at: datetime
    updated_at: datetime

    # Información de usuario
    user_email: Optional[str] = None
    user_username: Optional[str] = None

    # Información del cliente
    client_company: Optional[str] = None
    client_contact: Optional[str] = None

    # Información de la cotización (si existe)
    quote_number: Optional[str] = None

    # Items
    items: List[OrderItemResponse] = []

    model_config = ConfigDict(from_attributes=True)

    
