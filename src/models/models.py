from sqlalchemy import Column, Integer, String, MetaData, DateTime, func

from sqlalchemy.orm import declarative_base

metadata = MetaData()

Base = declarative_base(metadata=metadata)


class Currency(Base):
    __tablename__ = "currency"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    rate = Column(String, nullable=False)


class History_Currency(Base):
    __tablename__ = "history_currency"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    rate = Column(String, nullable=False)
    date_of_creation = Column(DateTime, default=func.current_timestamp())
