from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric, Text, Float, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base


class Producto(Base):
    """
        Modelo para los productos del sistema 
    """

    __tablename__ = "productos"

    # Identificador único
    id = Column(Integer, primary_key=True, index=True)

    # Información general
    nombre = Column(String(100), nullable=False, index=True)
    sku = Column(String(50), unique=True, nullable=False, index=True)
    descripcion = Column(Text,  nullable=False)
    categoria = Column(String(100), nullable=True, index=True)
    precio_base = Column(Numeric(10,2), nullable=True, default=0)
    stock = Column(Integer, nullable=True, default=0)

    # Relaciones con empresa Opcional
    empresa_id = Column(
        Integer,
        ForeignKey("empresas.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Estado
    activo = Column(Boolean, default=True, nullable=False)

    # Fechas de auditoría
    creado_en = Column(DateTime, default=func.now(), nullable=False)
    actualiado_en = Column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
        nullable=False
    )


    # Relaciones
    empresa = relationship("Empresa", back_populates="productos")

    def __repr__(self):
        """ Representación en string del prducto"""
        return f"< Producto {self.nombre} (SKU {self.sku})>"

    @property
    def precio_formateado(self):
        """ Propiedad calculada: precio con formato de moneda"""
        return f"${self.precio_base:,.2}" if self.precio_base else "$0.00"