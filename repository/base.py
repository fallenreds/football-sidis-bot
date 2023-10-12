from abc import ABC
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import Base
# from sqlalchemy.future import select
from sqlalchemy import update, select

from sqlalchemy.ext.asyncio import create_async_engine


class BaseRepositoryABC(ABC):
    def __init__(self, db_url):
        self.engine = create_async_engine(db_url, future=True)
        self.session = AsyncSession(self.engine, expire_on_commit=False)
    @staticmethod
    async def create(*args, **kwargs):
        pass

    @staticmethod
    async def get(*args, **kwargs):
        pass

    async def delete(self, *args, **kwargs):
        pass

    @staticmethod
    async def list(*args, **kwargs):
        pass



class BaseRepository(BaseRepositoryABC):
    model = Base

    async def create(self, **kwargs):
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.commit()
        return instance

    async def get(self, **kwargs):
        stmt = select(self.model).filter_by(**kwargs)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(self, **kwargs):
        stmt = select(self.model).filter_by(**kwargs)
        result = await self.session.execute(stmt)
        return result.scalars()

    async def delete(self, **kwargs):
        instances = await self.list(**kwargs)
        for instance in instances:
            await self.session.delete(instance)
        await self.session.commit()

    async def close(self):
        await self.session.close()
        await self.engine.dispose()

    async def update(self, update_data: dict, **filters):
        stmt = update(self.model).filter_by(**filters).values(update_data)
        await self.session.execute(stmt)
        await self.session.commit()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()