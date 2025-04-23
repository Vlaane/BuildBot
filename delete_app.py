from sqlalchemy.ext.asyncio import AsyncSession
from models.application import Application
from models.item import Item


async def delete_application_and_item(session: AsyncSession, application_id: int, item_id: int):
    try:
        # Удаляем запись из таблицы Application по ID
        application = await session.get(Application, application_id)
        if application:
            await session.delete(application)
            print(f"Запись из Application с ID {application_id} успешно удалена.")
        else:
            print(f"Запись из Application с ID {application_id} не найдена.")

        # Удаляем запись из таблицы Item по ID
        item = await session.get(Item, item_id)
        if item:
            await session.delete(item)
            print(f"Запись из Item с ID {item_id} успешно удалена.")
        else:
            print(f"Запись из Item с ID {item_id} не найдена.")

        await session.commit()
    except Exception as e:
        print(f"Ошибка при удалении записей: {e}")
        await session.rollback()


import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Создаем асинхронный движок и фабрику сессий
DATABASE_URL = "sqlite+aiosqlite:///database.db"
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def main():
    async with AsyncSessionLocal() as session:
        await delete_application_and_item(session, application_id=1, item_id=1)


asyncio.run(main())
