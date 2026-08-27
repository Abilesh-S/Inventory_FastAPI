from typing import Optional
from pydantic import BaseModel

class CustomerCreate(BaseModel):
    name: str
    phone: str
    address: Optional[str] = None

class CustomerOut(CustomerCreate):
    id: int
    class Config:
        from_attributes = True