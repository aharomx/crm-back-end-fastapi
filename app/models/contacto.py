from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base


class Contacto(Base):
    """
        Modelo para contactos individuales.
        Un contacto puede pertenecer a una empresa o ser independiente (B2C)
    """

    __tablename__ = "contactos"

    # Identificador
    id = Column(Integer, primary_key=True, index=True)

    # Relacion con empresa (Opcional)
    # Si es Null, el contacto es una empresa independiente
    empresa_id = Column(
        Integer,
        ForeignKey("empresas.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Información personal
    nombre = Column(String(100), nullable=False, index=True)
    apellido = Column(String(100), nullable=False)

    # Información Laboral
    cargo = Column(String(100), nullable=True)
    departamento = Column(String(100), nullable=True)

    # Información de contacto
    email = Column(String(150), nullable=False, unique=True, index=True)
    email_secundario = Column(String(150), nullable=True)
    telefono_movil = Column(String(20), nullable=True)
    telefono_fijo = Column(String(20), nullable=True)

    # Información adicional
    fecha_nacimiento = Column(Date, nullable=True)
    linkedin_url = Column(Text, nullable=True)
    notas = Column(Text, nullable=True)


    # Flags
    es_principal = Column(Boolean, default=False) # Contacto principal de la empresa
    activo = Column(Boolean, default=True, nullable=False)


    # Fechas
    creado_en = Column(DateTime, server_default=func.now(), nullable=False)
    actualizado_en = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relaciones
    empresa = relationship("Empresa", back_populates="contactos")

    def __repr__(self):
        return f"<Contacto {self.nombre} {self.apellido}>"

    @property
    def nombre_completo(self):
        """ Propiedad Calculada """
        return f"{self.nombre} {self.apellido}"
