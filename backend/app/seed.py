import asyncio

from sqlalchemy.dialects.postgresql import insert

from app.db.base import AppMetadata
from app.db.session import get_sessionmaker


async def seed() -> None:
    async_session = get_sessionmaker()
    async with async_session() as session:
        stmt = insert(AppMetadata).values(key="seed_version", value="foundation-v1")
        stmt = stmt.on_conflict_do_update(
            index_elements=[AppMetadata.key], set_={"value": "foundation-v1"}
        )
        await session.execute(stmt)
        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed())
