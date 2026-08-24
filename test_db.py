import asyncio
from app.core.database import AsyncSessionLocal
from sqlalchemy import text

async def test_db():
    try:
        async with AsyncSessionLocal() as session:
            result= await session.execute(text("SELECT 1"))
            print("Conexión exitosa")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "main":
    asyncio.run(test_db())