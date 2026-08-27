from pydantic import BaseModel
from datetime import datetime
from app.models.transaction import TransactionType

class TransactionCreate(BaseModel):
    product_id: int
    user_id: int
    quantity: int

class TransactionOut(BaseModel):
    id: int
    product_id: int
    user_id: int
    transaction_type: TransactionType
    quantity: int
    timestamp: datetime
    class Config:
        from_attributes = True