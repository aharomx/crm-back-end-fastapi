# Importar todos los modelo aqui para que SQLAlchemy los registre
from app.db.session import Base
from app.models.usuario import Usuario
from app.models.empresa import Empresa
from app.models.contacto import Contacto

# Esto permite que Alembic detecte todos los modelos
# y que Base.metadata tenga todas las tablas