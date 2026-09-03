from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from datetime import datetime, timedelta
from typing import List, Dict, Any

from app.models.prospect import Prospect
from app.models.client import Client
from app.models.call import Call
from app.models.appointment import Appointment
from app.models.quote import Quote
from app.models.order import Order
from app.schemas.dashboard import (
    ProspectMetrics,
    ClientMetrics,
    CallMetrics,
    AppointmentMetrics,
    QuoteMetrics,
    OrderMetrics,
    RecentActivity,
    Alert, 
    DashboardResponse
)

class DashboardService:
    def __init__(self, db:AsyncSession):
        self.db= db
        self.now= datetime.now()
        self.seven_days_ago = self.now - timedelta(days=7)

    async def get_prospect_metrics(self) -> ProspectMetrics:
        """ Obtiene métricas de prospectos """

        # Total
        total_result = await self.db.execute(select(func.count()).select_from(Prospect))
        total = total_result.scalar() or 0

        # Por status
        status_result = await self.db.execute(
            select(Prospect.status, func.count())
            .group_by(Prospect.status)
        )
        by_status = {status: count for status, count in status_result.all()}

        # Nuevos en los últimos 7 días
        new_result = await self.db.execute(
            select(func.count()).where(
                and_(
                    Prospect.created_at >= self.seven_days_ago,
                    Prospect.status != 'converted'
                )
            )
        )
        new_last_7_days = new_result.scalar() or 0

        # Valor estimado total
        value_result = await self.db.execute(
            select(func.sum(Prospect.estimated_value))
            .where(Prospect.estimated_value.isnot(None))
        )
        total_value = value_result.scalar() or 0.0

        # Tasa de conversión
        converted_result = await self.db.execute(
            select(func.count()).where(Prospect.status == 'converted')
        )
        converted = converted_result.scalar() or 0
        conversion_rate = (converted / total * 100) if total > 0 else 0.0

        return ProspectMetrics(
            total=total, 
            by_status=by_status,
            conversion_rate=round(conversion_rate,2),
            new_last_7_days= new_last_7_days,
            total_estimated_value=float(total_value)
        )

    async def get_client_metrics(self) -> ClientMetrics:
        """ Obtiene las métricas de clientes """

        # Total
        total_result = await self.db.execute(select(func.count()).select_from(Client))
        total = total_result.scalar() or 0

        # Por status
        status_result = await self.db.execute(
            select(Client.status, func.count())
            .group_by(Client.status)
        )
        by_status = {status: count for status, count in status_result.all()}

        # Por tipo
        type_result = await self.db.execute(
            select(Client.type, func.count())
            .group_by(Client.type)
        )
        by_type = {type: count for type, count in type_result.all()}


        # Nuevos en los últimos 7 días
        new_result = await self.db.execute(
            select(func.count())
            .where(Client.created_at >= self.seven_days_ago)
        )
        new_las_7_days = new_result.scalar() or 0

        return ClientMetrics(
            total=total,
            by_status=by_status,
            by_type=by_type,
            new_last_7_days=new_las_7_days
        )

    async def get_call_metrics(self, user_id: int) -> CallMetrics:
        """ Obtiene métricas de llamadas """

        # Total
        total_result = await self.db.execute(
            select(func.count())
            .where(Call.user_id == user_id)
        )
        total = total_result.scalar() or 0

        # Por tipo
        type_result = await self.db.execute(
            select(Call.type, func.count())
            .where(Call.user_id == user_id)
            .group_by(Call.type)
        )
        by_type = {type: count for type, count in type_result.all()}

        # Por status
        status_result = await self.db.execute(
            select(Call.status, func.count())
            .where(Call.user_id == user_id)
            .group_by(Call.status)
        )
        by_status = {status: count for status, count in status_result.all()}

        # Llamadas recientes (últimos 7 días)
        recent_result = await self.db.execute(
            select(func.count())
            .where(
                and_(
                    Call.user_id == user_id,
                    Call.call_date >= self.seven_days_ago
                )
            )
        )
        recent_calls = recent_result.scalar() or 0

        # Duración promedio
        avg_results = await self.db.execute(
            select(func.avg(Call.duration_minutes))
            .where(Call.user_id == user_id)
        )
        avg_duration = avg_results.scalar() or 0.0

        return CallMetrics(
            total= total,
            by_type=by_type,
            by_status=by_status,
            recent_calls=recent_calls,
            avg_duration_minutes=round(float(avg_duration),2)
        )

    async def get_appointment_metrics(self, user_id:int) -> AppointmentMetrics:
        """ Obtiene métricas de citas """

        # Total
        total_result = await self.db.execute(
            select(func.count())
            .where(Appointment.user_id == user_id)
        )
        total= total_result.scalar() or 0

        # Por status
        status_result = await self.db.execute(
            select(Appointment.status, func.count())
            .where(Appointment.user_id == user_id)
            .group_by(Appointment.status)
        )
        by_status = {status: count for status, count in status_result.all()}

        # Por prioridad
        priority_result = await self.db.execute(
            select(Appointment.priority, func.count())
            .where(Appointment.user_id == user_id)
            .group_by(Appointment.priority)
        )
        by_priority = {priority: count for priority, count in priority_result.all()}

        # citas de hoy
        today_start = self.now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        today_result = await self.db.execute(
            select(func.count())
            .where(
                and_(
                    Appointment.user_id == user_id,
                    Appointment.start_datetime >= today_start,
                    Appointment.start_datetime <= today_end
                )
            )
        )
        today_count = today_result.scalar() or 0

        # Próximas citas (7 días)
        future = self.now + timedelta(days=7)
        upcoming_result = await self.db.execute(
            select(func.count())
            .where(
                and_(
                    Appointment.user_id == user_id,
                    Appointment.start_datetime >= self.now,
                    Appointment.start_datetime <= future, 
                    Appointment.status.in_(['scheduled', 'confirmed'])
                )
            )
        )
        upcoming_count = upcoming_result.scalar() or 0

        return AppointmentMetrics(
            total=total,
            by_status=by_status,
            by_priority=by_priority,
            today_count=today_count,
            upcoming_count=upcoming_count
        )


    async def get_quote_metrics(self, user_id: int) -> QuoteMetrics:
        """ Obtiene métricas de cotizaciones """

        # Total
        total_result = await self.db.execute(
            select(func.count())
            .where(Quote.user_id == user_id)
        )
        total = total_result.scalar() or 0

        # Por status
        status_result = await self.db.execute(
            select(Quote.status, func.count())
            .where(Quote.user_id == user_id)
            .group_by(Quote.status)
        )
        by_status = {status: count for status, count in status_result.all()}

        #Valor total
        value_result = await self.db.execute(
            select(func.sum(Quote.total))
            .where(Quote.user_id == user_id)
        )
        total_value = value_result.scalar() or 0.0

        # Valor aceptado
        accepted_result = await self.db.execute(
            select(func.sum(Quote.total))
            .where(
                and_(
                    Quote.user_id == user_id,
                    Quote.status == 'accepted'
                )
            )
        )
        accepted_value = accepted_result.scalar() or 0.0

        # Tasa de conversión
        accepted_count = by_status.get('accepted',0)
        conversion_rate = (accepted_count / total * 100) if total > 0 else 0.0

        return QuoteMetrics(
            total=total,
            by_status=by_status,
            total_value=float(total_value),
            accepted_value=float(accepted_value),
            conversion_rate=round(conversion_rate,2)
        )

    async def get_order_metrics(self, user_id:int) -> OrderMetrics:
        """ Obtiene métricas de pedidos """

        # Total
        total_result = await self.db.execute(
            select(func.count())
            .where(Order.user_id == user_id)
        )
        total = total_result.scalar() or 0

        # Por status
        status_result = await self.db.execute(
            select(Order.status, func.count())
            .where(Order.user_id == user_id)
            .group_by(Order.status)
        )
        by_status = {status: count for status, count in status_result.all()}

        # Por prioridad
        priority_result = await self.db.execute(
            select(Order.priority, func.count())
            .where(Order.user_id == user_id)
            .group_by(Order.priority)
        )
        by_priority = {priority: count for priority, count in priority_result.all()}

        # Valor total
        value_result = await self.db.execute(
            select(func.sum(Order.total))
            .wherer(Order.user_id == user_id)
        )
        total_value = value_result.scalar() or 0.0

        # Valor entregado
        delivered_result = await self.db.execute(
            select(func.sum(Order.total))
            .where(
                and_(
                    Order.user_id == user_id,
                    Order.status == 'delivered'
                )
            )
        )
        delivered_value = delivered_result.scalar() or 0.0

        return OrderMetrics(
            total=total,
            by_status=by_status,
            by_priority=by_priority,
            total_value= float(total_value),
            delivered_value=float(delivered_value)
        )

    async def get_recent_activity(self, user_id:int, limit: int=10) -> List[RecentActivity]:
        """ Obtiene la actividad reciente del usuario """

        activities = []

        # Obtener últimos prospectos
        prospects = await self.db.execute(
            select(Prospect)
            .where(Prospect.created_by_id == user_id)
            .order_by(desc(Prospect.created_at))
            .limit(limit // 2)
        )
        for p in prospects.scalars().all():
            activities.append(RecentActivity(
                type="prospect",
                action="created",
                description=f"Nuevo prospecto: {p.company_name}",
                entity_id=p.id,
                entity_name=p.company_name,
                created_at=p.created_at,
                user_id=user_id,
                user_name=""
            ))

        # Obtener últimos clientes
        clients = await self.db.execute(
            select(Client)
            .where(Client.created_by_id == user_id)
            .order_by(desc(Client.created_at))
            .limit(limit // 2)
        )
        for c in clients.scalars().all():
            activities.append(RecentActivity(
                type="client",
                action="created",
                description=f"Nuevo cliente: {c.company_name}",
                entity_id=c.id,
                entity_name=c.company_name,
                created_at=c.created_at,
                user_id= user_id,
                user_name=""
            ))

        # Obtener últimas llamadas
        calls = await self.db.execute(
            select(Call)
            .where(Call.user_id == user_id)
            .order_by(desc(Call.call_date))
            .limit(limit // 2)
        )
        for c in calls.scalars().all():
            target = c.prospect.company_name if c.prospect else c.client.company_name if c.client else "Contacto"
            activities. append(RecentActivity(
                type="call",
                action="created",
                description=f"Llamada: {c.subject} con {target}",
                entity_id=c.id,
                entity_name=target,
                created_at=c.call_date,
                user_id=user_id,
                user_name=""
            ))

        # Ordernar por fechas
        activities.sort(key=lambda x: x.created_at, reverse=True)

        return activities[:limit]

    async def get_alerts(self, user_id:int) -> List[Alert]:
        """ Obtiene alertas por usuario """
        alerts = []

        # Alertas de citas próximas (Menos de 24 horas)
        tomorrow = self.now + timedelta(days=1)
        appointments = await self.db.execute(
            select(Appointment)
            .where(
                and_(
                    Appointment.user_id == user_id,
                    Appointment.start_datetime >= self.now,
                    Appointment.start_datetime <= tomorrow,
                    Appointment.status.in_(['scheduled', 'confirmed'])
                )
            )
            .order_by(Appointment.start_datetime.asc())
        )

        for apt in appointments.scalars().all():
            hours = (apt.start_datetime - self.now).total_seconds() / 3600
            if hours <24:
                alerts.append(Alert(
                    type="warning",
                    message=f"📅 Cita en {int(hours)} horas: {apt.title}",
                    link=f"/appointments/{apt.id}",
                    created_at=self.now
                ))

        # Alertas de cotizaciones por vencer (menos de 7 días)
        week_from_now = self.now + timedelta(days=7)
        quotes = await self.db.execute(
            select(Quote)
            .where(
                and_(
                    Quote.user_id == user_id,
                    Quote.expiry_date >= self.now,
                    Quote.expiry_date <= week_from_now,
                    Quote.status == 'sent'
                )
            )
            .order_by(Quote.expiry_date.asc())
        )

        for quote in quotes.scalars().all():
            days = (quote.expiry_date - self.now).days
            alerts.append(Alert(
                type="info",
                message=f"📄 Cotización {quote.quote_number} vence en {days} días",
                link = f"/quotes/{quote.id}",
                created_at= self.now
            ))


        # Alertas de prospectos sin seguimiento (más de 7 días sin contacto)
        week_ago = self.now - timedelta(days=7)
        old_prospects = await self.db.execute(
            select(Prospect)
            .where(
                and_(
                    Prospect.created_by_id == user_id,
                    Prospect.updated_at <= week_ago,
                    Prospect.status.in_(['new','contacted'])
                )
            )
        )

        for p in old_prospects.scalars().all():
            alerts.append(Alert(
                type="danger",
                meesage= f"⚠️ {p.company_name} necesita seguimiento (sin contacto en 7+ días)",
                link= f"/prospects/{p.id}",
                created_at=self.now
            ))

        return  alerts


    async def get_dashboard(self, user_id: int) -> DashboardResponse:
        """ Obtiene el dashboard completo """

        # Obtener todas las métricas en paralelo
        prospects = await self.get_prospect_metrics()
        clients = await self.get_client_metrics()
        calls = await self.get_call_metrics( user_id)
        appointments = await self.get_appointment_metrics(user_id)
        quotes = await self.get_quote_metrics(user_id)
        orders = await self.get_order_metrics(user_id)

        # Actividad reciente y alertas
        recent_activity = await self.get_recent_activity(user_id)
        alerts = await self.get_alerts(user_id)

        return DashboardResponse(
            prospects= prospects,
            client= clients,
            calls=calls,
            appointments=appointments,
            quotes=quotes,
            orders=orders,
            recent_activity=recent_activity,
            alerts=alerts
        )
    

    
