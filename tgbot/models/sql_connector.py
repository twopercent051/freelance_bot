from sqlalchemy import MetaData, inspect, Column, String, insert, select, update, Integer, Date, Boolean
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, as_declarative

from create_bot import DATABASE_URL

engine = create_async_engine(DATABASE_URL)

async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@as_declarative()
class Base:
    metadata = MetaData()

    def _asdict(self):
        return {c.key: getattr(self, c.key)
                for c in inspect(self).mapper.column_attrs}


class MyProjects(Base):
    """Заявки на просмотр общего каталога"""
    __tablename__ = 'my_projects'

    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    # description = Column(String, nullable=True)
    royalty = Column(Integer, nullable=False, server_default="0")
    start_date = Column(Date, nullable=False)
    finish_date = Column(Date, nullable=True)
    worktime = Column(Integer, nullable=False, server_default="0")  # Число минут
    is_finished = Column(Boolean, nullable=False, server_default="false")
    # one_hour_price = Column(Integer, nullable=True)


class MyProjectsDAO(MyProjects):
    """Класс взаимодействия с БД"""
    @classmethod
    async def create(cls, **data):
        async with async_session_maker() as session:
            stmt = insert(MyProjects).values(**data)
            await session.execute(stmt)
            await session.commit()

    @classmethod
    async def change_worktime(cls, project_id: int, worktime: int):
        async with async_session_maker() as session:
            stmt = update(MyProjects).filter_by(id=project_id).values(worktime=MyProjects.worktime+worktime)
            await session.execute(stmt)
            await session.commit()

    @classmethod
    async def change_data(cls, project_id: int, **data):
        async with async_session_maker() as session:
            stmt = update(MyProjects).filter_by(id=project_id).values(**data)
            await session.execute(stmt)
            await session.commit()

    @classmethod
    async def get_all(cls, all_projects: bool) -> list:
        async with async_session_maker() as session:
            if all_projects:
                query = select(MyProjects.__table__.columns).order_by(MyProjects.id.desc())
            else:
                query = select(MyProjects.__table__.columns).order_by(MyProjects.id.desc()).filter_by(is_finished=False)
            result = await session.execute(query)
            return result.mappings().all()

    @classmethod
    async def get_one_or_none(cls, project_id: int) -> dict:
        async with async_session_maker() as session:
            query = select(MyProjects.__table__.columns).filter_by(id=project_id)
            result = await session.execute(query)
            return result.mappings().one_or_none()
