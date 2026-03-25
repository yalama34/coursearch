from sqlalchemy.ext.asyncio import create_async_engine

from config import DATABASE_URL


engine = create_async_engine(
    DATABASE_URL,
    echo=False,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def get_session():
    async with async_session_maker() as session:
        yield session
