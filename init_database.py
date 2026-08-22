"""
    Script paar inicializar la base de datos
    Uso:
        python init_database.py           # Crear tablas
        python init_database.py --seed    # Crear tablas + datps de prueba
        python init_database.py --drop    # eliminar todas las tablas
"""

import sys
from app.db.session import SessionLocal
from app.db.init_db import init_db, seed_db, drop_db

def main():
    # Parsear argumentos
    args = sys.argv[1:]

    # Crear sesión
    db= SessionLocal()

    try:
        if "--drop" in args:
            print("⚠️ Eliminando todas las tablas ")
            drop_db()
            print("✅ Tablas Eliminadas")
            return

        # Crear tablas
        print("🔨 Creando tablas")
        init_db(db)

        # Insertar datos de prueba si se solicita
        if "--seed" in args:
            print("🌱 Insertando datos de prueba")
            seed_db(db)

        print("✅ Proceso completado")
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()