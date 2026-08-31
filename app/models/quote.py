from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Quote(BaseModel):
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True, index=True)

    # Relación con prospecto (opcional)
    prospect_id = Column(Integer, ForeignKey("prospect.id"), nullable=True)
    prospect = relationship("Prospect", foreign_keys=[prospect_id])

    # Relación con el cliente
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    client = relationship("client", foreign_keys=[client_id])

    # Usuario que crea la cotización
    user_id = Column(Integer, ForeignKey("user_id"), nullable=False)
    user = relationship("User", foreign_keys=[user_id])

    # Datos de la cotización
    quote_number = Column(String(50), nullable=False, unique=True)
    title = Column(String(255), nullable=False)
    issue_date = Column(DateTime, nullable=False)
    expiry_date = Column(DateTime, nullable=False)

    # Totales
    subtotal = Column(Float, default=0.0)
    tax = Column(Float, default=0.0)
    discount = Column(Float, default=0.0)
    total = Column(Float, default=0.0)

    # Estado
    status = Column(String(50), default="draft") # draft, sent, accepted, rejected, expired

    # Notas y términos
    notes = Column(Text, nullable=True)
    terms = Column(Text, nullable=True)

    # Relación con item
    items = relationship("QuoteItem", back_populates="quote", cascade="all, delete-orphan")


class QuoteItem(BaseModel):
    __tablename__ = "quote_items"

    id = Column(Integer, ForeignKey("quotes.id"), nullable=False)
    quote = relationship("Quote", back_populates="items")

    # Datos del item
    description = Column(String(500), nullable=False)
    quantity = Column(Float, default=1.0)
    unit_price = Column(Float, default=0.0)
    total = Column(Float, default=0.0)

    


