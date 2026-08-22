from sqlalchemy.orm import Session
from app.db.session import Base, engine
from app.models.usuario import Usuario
from app.models.contacto import Contacto
from  app.models.empresa import Empresa
from app.models.producto import Producto

def init_db(db: Session) -> None:
    """
        Inicializar la base de datos creando todas las tablas
    """

    # Crear todas las tablas definicas en los modelos
    Base.metadata.create_all(bind=engine)
    print( "✅ Tablas Creadas exitósamente")

def drop_db() -> None:
    """
        Eliminar todas las tablas (util para desarrollo)
        NO USAR EN PRODUCCION
    """
    Base.metadata.drop_all(bind=engine)
    print("⚠️ Todas las tablas fueron eliminadas")

def seed_db(db: Session) -> None:
    """
        Insertar datos de prubea
    """
    if db.query(Usuario).count() > 0:
        print("ℹ️ La base de datos ya tiene datos. Saltando seed....")
        return

    # Crear usuarios de prueba

    usuarios = [
        Usuario(
            nombre="Admin",
            apellido="Principal",
            email="admin@crm.com",
            password_hash = "hash_temporal", # Despues cambiarmos por bcryt
            rol= "Admin",
            meta_mensual= None,
        ),
        Usuario(
            nombre="Juan",
            apellido="Pérez",
            email="juan.perez@crm.com",
            password_hash="hash_temporal",
            rol="Vendedor",
            meta_mensual=100000,
        ),
        Usuario(
            nombre="María",
            apellido="González",
            email="maria.gonzalez@crm.com",
            password_hash="hash_temporal",
            rol="Vendedor",
            meta_mensual=120000,
        ),
    ]

    db.add_all(usuarios)
    db.commit()

    # Crear empresas de prueba
    empresas = [
        Empresa(
            razon_social="Tech Solutions SA de CV",
            rfc_tax_id="TEC123456ABC",
            tipo="Cliente Activo",
            sector="Tecnología",
            tamano_empresa="Mediana",
            telefono_principal="555-123-4567",
            sitio_web="https://techsolutions.com",
            ciudad="Ciudad de México",
            pais="México",
        ),
        Empresa(
            razon_social="Industrias del Norte",
            rfc_tax_id="IND789012XYZ",
            tipo="Prospecto",
            sector="Manufactura",
            tamano_empresa="Grande",
            telefono_principal="818-555-7890",
            sitio_web="https://industriasnorte.com",
            ciudad="Monterrey",
            pais="México",
        ),
    ]

    db.add_all(empresas)
    db.commit()

    # Crear contactos de prueba
    contactos = [
        Contacto(
            empresa_id=1,  # Tech Solutions
            nombre="Carlos",
            apellido="Ramírez",
            cargo="Director de TI",
            departamento="Tecnología",
            email="carlos.ramirez@techsolutions.com",
            telefono_movil="555-111-2222",
            es_principal=True,
        ),
        Contacto(
            empresa_id=1,  # Tech Solutions
            nombre="Laura",
            apellido="Martínez",
            cargo="Gerente de Compras",
            departamento="Compras",
            email="laura.martinez@techsolutions.com",
            telefono_movil="555-333-4444",
            es_principal=False,
        ),
        Contacto(
            empresa_id=2,  # Industrias del Norte
            nombre="Pedro",
            apellido="Sánchez",
            cargo="Gerente General",
            email="pedro.sanchez@industriasnorte.com",
            telefono_movil="818-555-6666",
            es_principal=True,
        ),
        # Contacto independiente (sin empresa)
        Contacto(
            empresa_id=None,
            nombre="Ana",
            apellido="López",
            cargo="Consultora Independiente",
            email="ana.lopez@gmail.com",
            telefono_movil="555-777-8888",
            es_principal=False,
        ),
    ]

    db.add_all(contactos)
    db.commit()

    productos = [
        Producto(
            nombre="Software CRM Licencia Anual",
            sku="SW-CRM-001",
            descripcion="Licencia anual del software CRM",
            categoria="Software",
            precio_base=12000.00,
            stock=100,
        ),
        Producto(
            nombre="Servicio de Implementación",
            sku="SRV-IMP-001",
            descripcion="Servicio de implementación y configuración",
            categoria="Servicios",
            precio_base=15000.00,
            stock=None,  # Los servicios no tienen stock
        ),
    ]
    db.add_all(productos)
    db.commit()

    print(" Datos de prueba insertado exitosamente")
    print(f"      - Usuarios: {db.query(Usuario).count()}")
    print(f"      - Empresas: {db.query(Empresa).count()}")
    print(f"      - Contactos: {db.query(Contacto).count()}")

