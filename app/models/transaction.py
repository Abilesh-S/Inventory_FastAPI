import enum
from sqlalchemy import Column, Integer, ForeignKey, Enum, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class TransactionType(str, enum.Enum):
    STOCK_IN = "STOCK_IN"
    SALE = "SALE"

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    quantity = Column(Integer, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())