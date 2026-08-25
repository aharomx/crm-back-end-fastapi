# app/models/prospect.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Prospect(BaseModel):
    __tablename__ = "prospects"
    
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), nullable=False)
    contact_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    website = Column(String(255), nullable=True)
    status = Column(String(50), default="new")  # ✅ Usar String en lugar de Enum
    source = Column(String(50), default="other")  # ✅ Usar String en lugar de Enum
    notes = Column(Text, nullable=True)
    estimated_value = Column(Float, nullable=True)
    
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_by = relationship("User", foreign_keys=[created_by_id])