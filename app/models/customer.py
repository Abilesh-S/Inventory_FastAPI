from sqlalchemy import Column, Integer, String
from app.db.base import Base

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False, index=True)
    address = Column(String, nullable=True)