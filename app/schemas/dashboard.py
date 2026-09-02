from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any


# -------------------- Métricas Individuales --------------
class ProspectMetrics(BaseModel):
    total: int
    by_status: Dict[str,int]
    conversion_rate: float = Field(..., description= "Tasa de conversión a clientes (%)")
    new_last_7_days: int
    total_estimated_value: float


class ClientMetrics(BaseModel):
    total: int
    by_status: Dict[str, int]
    by_type: Dict[str, int]
    new_last_7_days: int


class CallMetrics(BaseModel):
    total:int
    by_type: Dict[str, int]  # incoming, outgoing
    by_status: Dict[str, int] # completed, pending, missed
    recent_calls: int # Últimos 7 días
    avg_duration_minutes: float

class AppointmentMetrics(BaseModel):
    total: int 
    by_status: Dict[str, int] # scheduled, confirmed, completed, cancelled, rescheduled
    by_priority: Dict[str, int] # low, medium, hight
    today_count: int
    upcoming_count: int # Próximos 7 días

class QuoteMetrics(BaseModel):
    total: int 
    by_status: Dict[str, int] # draft, sent, accepted, rejected, expired
    total_value: float
    accepted_value: float
    conversin_rate: float = Field(..., description="Tasa de conversión a pedido (%)")


class OrderMetrics(BaseModel):
    total: int 
    by_status: Dict[str, int] # draft, confirmed, in_progress, shipped, delivered, cancelled
    by_priority: Dict[str,int] # low, medium, high
    total_value: float
    delivered_value: float


# ----------------- Actividad Reciente -------------------
class RecentActivity(BaseModel):
    type: str # Prospect, client, call, appointment, quote, order
    action: str # created, updated, status_changed, etc.
    description: str
    entity_id: int
    entity_name: str 
    created_at: datetime
    user_id: int 
    user_name: str 


# ---------------- Alertas -----------------------------
class Alert(BaseModel):
    type: str # warning, info, success, danger
    message: str
    link: Optional[str] = None
    created_at: datetime

# --------------- Dashboard Completo -------------------
class DashboardResponse(BaseModel):
    # Métricas por módulo
    prospects: ProspectMetrics
    client: ClientMetrics
    calls: ClientMetrics
    appointments: AppointmentMetrics
    quotes: QuoteMetrics
    orders: OrderMetrics

    # Actividad reciente
    recent_activity: List[RecentActivity] = []

    # Alertas
    alerts: List[Alert] = []

    # Timestamp
    generated_at: datetime = Field(default_factory=datetime.now)
    