from pydantic import BaseModel

class ProductBase(BaseModel):
    name: str
    sku: str
    price: float

class ProductCreate(ProductBase):
    quantity: int = 0

class ProductOut(ProductBase):
    id: int
    quantity: int
    class Config:
        from_attributes = True

class StockUpdate(BaseModel):
    quantity: int