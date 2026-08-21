from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base


class Usuario(Base):
    """
        Modelo para los usuarios del sistema (vendedores, gerentes, admin)
    """

    __tablename__ = "usuarios"

    # Identificador único
    id = Column(Integer, primary_key=True, index=True)

    # Información personal
    nombre = Column(String(100), nullable=False, index=True)
    apellido = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    telefono = Column(String(20), nullable=True)

    # Autenticación
    password_hash = Column(Column(String(255), nullable=False))

    # Rol del uuario: Admin, Gerente, Vendedor, Soporte
    rol = Column(String(20), nullable=False, default="Vendedor")

    # Menta mensual de ventas (Para vendedores)
    meta_mensual = Column(Numeric(15,2), nullable=True)

    # Estado
    activo = Column(Boolean, default=True, nullable=False)

    # Fechas de auditoria
    creado_en = Column(DateTime, server_default=func.now(), nullable=False)
    actualizado_en = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    
    # Relaciones con otros modelos
    # Un usuario puede tener mcuhas oportunidades asigandas
    oportunidades = relationship("Oportunidad", back_populates="vendedor_asignado")

    # Un usuario puede hacer muchas llamadas
    llamadas = relationship("Llamada", back_populates="vendedor")

    def __repr__(self):
        """Representación en stgring del objeto"""
        return f"<Usuario {self.nombre} {self.apellido} ({self.email})>"

    @property
    def nombre_completo(self):
        """Propiedad calcualda: nombre completo"""
        return f"{self.nombre} {self.apellido}"