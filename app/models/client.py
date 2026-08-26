from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Client(BaseModel):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), nullable=False)
    contact_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    website = Column(String(255), nullable= True)

    # Tipos y status (strings con valores predefinidos)
    type = Column(String(50), default="company") # Company or individual
    status = Column(String(50), default="active") # active, inactive, archived
    industry = Column(String(100), nullable=True) # tech, retail, healthcare, etc

    # Dirección
    address = Column(Text,nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)

    notes = Column(Text, nullable=True)

    # Relación con el prospecto original (si existe)
    original_prospect_id = Column(Integer, ForeignKey("prospects.id"), nullable=True)
    original_prospect = relationship("Prospect", foreign_keys=[original_prospect_id])

    # Relación con el usuario que creó el cliente
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_by = relationship("User", foreign_keys=[created_by_id])

    # Relación con pedidos (uno a muchos)
    #orders = relationship("Order", back_populates="client", cascade="all, delete-orphan")