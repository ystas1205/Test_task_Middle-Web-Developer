from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from src.config import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME



engine = create_async_engine(
    f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)



async def get_async_session():
    async with Session() as session:
        yield session
