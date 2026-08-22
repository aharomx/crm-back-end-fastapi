from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """ Configuración de la aplicación """


    # Nombre del proyecto
    PROJECT_NAME: str = "CRM Ventas"
    API_V1_STR: str = "/api/v1"


    # Configuración de PostreSQL
    #POSTGRES_SERVER: str = "localhost"
    #POSTGRES_PORT: str = "5433" # puerto que se configuró en el wsl
    #POSTGRES_USER: str = "postgres"
    #POSTGRES_PASSWORD: str = "postgres"
    #POSTGRES_DB: str = "crm_ventas"

    # Usaremos  SQLite para desarrollo
    DATABASE_URL: str= "sqlite:///./crm_ventas.db"

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return self.DATABASE_URL
    
    # URL de conexión (se contruye automáticamente)
    #@property
    #def DATABASE_URL(self) -> str:
    #    """ Construir la URL de conexión a PosrgreSQL"""
    #    return(
    #        f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
    #        f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    #    )

    # Configuración de seguridad
    SECRET_KEY: str = "Clave-secreta-que-vamos-a-generar"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = True


# Instancia global de configuración
settings = Settings()