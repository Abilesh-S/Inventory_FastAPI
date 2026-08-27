from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.product import Product
from app.models.transaction import Transaction, TransactionType
from app.schemas.product import ProductCreate, ProductOut, StockUpdate

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/products", response_model=ProductOut)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    if db.query(Product).filter(Product.sku == product.sku).first():
        raise HTTPException(400, "SKU already exists")
    new_product = Product(**product.dict())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@router.post("/products/{product_id}/add-stock", response_model=ProductOut)
def add_stock(product_id: int, stock: StockUpdate, user_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404, "Product not found")
    product.quantity += stock.quantity
    db.add(Transaction(product_id=product.id, user_id=user_id,
                        transaction_type=TransactionType.STOCK_IN, quantity=stock.quantity))
    db.commit()
    db.refresh(product)
    return product