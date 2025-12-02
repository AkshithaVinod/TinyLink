# from sqlalchemy import column, Integer, String, DateTime, func
# from .database import Base

# class URL(Base):
#     __tablename__ = "urls"

#     id = column(Integer, primary_key=True, index=True)
#     short_code = column(String, unique=True, index=True, nullable=False)
#     original_url = column(String, nullable=False)
#     clicks = column(Integer, default=0)
#     created_at = column(DateTime(timezone=True), server_default=func.now())

# app/models.py
from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class URL(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    short_code = Column(String, unique=True, index=True, nullable=False)
    original_url = Column(String, nullable=False)
    clicks = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())