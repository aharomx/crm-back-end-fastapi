from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base


class Empresa(Base):
    """
        Model para empresa clientes (B2B).
        También puede representar clientes individuales
    """

    __tablename__ ="empresas"

    # Identificador
    id = Column(Integer, primary_key=True, index=True)

    # información principal
    razon_social = Column(String(200), nullable=True, index=True)
    rfc_tax_id = Column(String(50), unique=True, nullable=True)

    # Tipo de empresa
    # Prospecto: Aún no es cliente
    # Cliente Activo: Ya ha comprado
    # Inactivo: No ha comprado recientemente
    # Perdido: se fue con la competencia
    tipo = Column(String(20), nullable=False, default="Prospecto", index=True)

    # Sector industrial
    sector = Column(String(100), nullable=True)

    # Tamaño de la empresa
    # Micro, Pequeña, Mediana, Grande, Corporativa
    tamano_empresa = Column(String(50), nullable=True)

    # Información de contacto
    telefono_principal = Column(String(20), nullable=True)
    sitio_web = Column(String(100), nullable=True)

    # Dirección
    direccion = Column(Text, nullable=True)
    ciudad = Column(String(100), nullable=True)
    estado_provincia = Column(String(100), nullable=True)
    pais = Column(String(100), nullable=True, default="México")

    # Estado
    activo = Column(Boolean, default=True, nullable=False)

    # Fechas
    creado_en = Column(DateTime, server_default=func.now(), nullable=False)
    actualizado_en = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )


    # relaciones
    # Una empresa tiene muchos contactos
    contactos = relationship("Contacto", back_populates="empresa")

    # Agregar relación con productos
    productos = relationship("Producto", back_populates="empresa")

    # Una empresa puede tener mcuhas oportunidades
    #oportunidades = relationship("Oportunidad", back_populates="empresa")

    def __repr__(self):
        return f"<Empresa {self.razon_social}>"    