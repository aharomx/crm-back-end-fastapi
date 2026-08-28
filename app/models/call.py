from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Call(BaseModel):
    __tablename__ = "calls"

    id = Column(Integer, primary_key=True, index=True)

    # Relación con prospectos (opcional)
    prospect_id = Column(Integer, ForeignKey("prospects.id"), nullable=True)
    prospect = relationship("Prospect", foreign_keys=[prospect_id])

    # Relación con cliente (Opcional)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    client = relationship("Client", foreign_keys=[client_id])

    # Usuario que realizó la llamada
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", foreign_keys=[user_id])

    # Datos de la llamada
    call_date = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, nullable=True) # Duración en minutos
    subjects = Column(String(255), nullable=False)
    notes = Column(Text, nullable=True)
    next_action = Column(Text, nullable=True) # Próximo paso a seguir

    # Tipos y status
    type = Column(String(50), default="outgoing") # incoming, outgoing
    status = Column(String(50), default="completed") # completed, pending
    direction = Column(String(50), default="outbound") # inbound, outbound

    # Calificación de llamada (opcional)
    rating = Column(Integer, nullable=True) # 1-5 estrellas
    