from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    name: str
    sku: str
    price: float


class ProductCreate(ProductBase):
    quantity: int = Field(default=0, ge=0)


class ProductOut(ProductBase):
    id: int
    quantity: int

    class Config:
        from_attributes = True


class StockUpdate(BaseModel):
    quantity: int = Field(gt=0)