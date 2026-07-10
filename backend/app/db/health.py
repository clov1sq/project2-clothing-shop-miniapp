from sqlalchemy import text

from app.db.session import get_sessionmaker


async def check_database() -> bool:
    async_session = get_sessionmaker()
    async with async_session() as session:
        await session.execute(text("SELECT 1"))
    return True
