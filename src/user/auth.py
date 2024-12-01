from fastapi.params import Depends
from fastapi_users.authentication import CookieTransport, AuthenticationBackend
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable, \
    SQLAlchemyUserDatabase

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, declarative_base

from sqlalchemy import Boolean, String, func, Integer, MetaData, Column

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime

from src.database import get_async_session
from fastapi_users.authentication import JWTStrategy

Base: DeclarativeBase = declarative_base()
metadata = MetaData()

from fastapi_users.authentication import BearerTransport

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

# cookie_transport = CookieTransport(cookie_name="cars", cookie_max_age=3600)

SECRET = "SECRET"


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

class User(SQLAlchemyBaseUserTable[int], Base):
    id = Column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(
        String(length=320), unique=True, index=True, nullable=False
    )
    username: Mapped[str] = mapped_column(String(length=100), nullable=False)
    hashed_password: Mapped[str] = mapped_column(
        String(length=1024), nullable=False
    )
    registered_ad: Mapped[DateTime] = mapped_column(DateTime,
                                                    default=func.current_timestamp())


    is_active: Mapped[bool] = mapped_column(Boolean, default=True,
                                            nullable=False)
    is_superuser: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session,User)