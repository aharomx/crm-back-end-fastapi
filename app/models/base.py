from sqlalchemy import Column, DateTime, func
from sqlalchemy.ext.declarative import declared_attr
from app.core.database import Base


class TimestampMixin:
    """ Mixin que añade timestamps a los modelos"""

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

class BaseModel(Base, TimestampMixin):
    """ Modelo base con timestamping automáticos """

    __abstract__ = True # No crea tabla para esta clase

    @declared_attr
    def __tablename__(cls):
        return cls.name.lower() # Pone los nombres de tablas en minúsculas