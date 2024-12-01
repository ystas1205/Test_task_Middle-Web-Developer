
from sqlalchemy import Column, Integer, String, Numeric, \
    MetaData, func, Boolean, DateTime

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import Mapped, mapped_column
metadata = MetaData()

Base = declarative_base(metadata=metadata)


class User(Base):
    __tablename__ = "user"

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
