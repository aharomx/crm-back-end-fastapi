from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, Boolean
from sqlalchemy.orm  import Relationship
from app.models.base import BaseModel


class Appointment(BaseModel):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)

    # Relación con prospecto (opcional)
    prospect_id = Column(Integer, ForeignKey("prospect_id"), nullable=True)
    prospect  = Relationship("Prospect", foreign_keys=[prospect_id])

    # Relación con cliente (opcional)
    client_id = Column(Integer, ForeignKey("client_id"), nullable= True)
    client = Relationship("Client", foreign_keys=[client_id])

    # Usuario que agenda la cita
    user_id = Column(Integer, ForeignKey("user_id"), nullable=False)
    user = Relationship("User", foreign_keys=[user_id])

    # Datos de la cita
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime, nullable=False)

    # Ubicación y enlace
    location = Column(String(50), default="online") # online, office, client_site, phone
    meeting_link = Column(String(500), nullable=True)

    # Estado y prioridad
    status = Column(String(50), default="scheduled") # scheduled, confirmed, completed, cancelled, rescheduled
    priority = Column(String(50), default="medium") # low, medium, high

    # Recordatorio (minutos antes)
    reminder_minutes = Column(Integer, default=15)
    reminder_sent = Column(Boolean, default=False)

    # Notas adicionales
    notes = Column(Text, nullable=True)