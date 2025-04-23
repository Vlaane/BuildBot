from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import config

# Создание базы даных

Base = declarative_base()
engine = create_async_engine(config.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    class_=AsyncSession,
    bind=engine,
)


# Инициализация бд
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

