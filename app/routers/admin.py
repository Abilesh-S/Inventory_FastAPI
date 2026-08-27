from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.product import Product
from app.models.transaction import Transaction, TransactionType
from app.models.user import User, RoleEnum
from app.schemas.product import ProductCreate, ProductOut, StockUpdate
from app.core.dependencies import require_role

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/products", response_model=ProductOut)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.ADMIN)),
):
    if db.query(Product).filter(Product.sku == product.sku).first():
        raise HTTPException(400, "SKU already exists")
    new_product = Product(**product.dict())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@router.post("/products/{product_id}/add-stock", response_model=ProductOut)
def add_stock(
    product_id: int,
    stock: StockUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.ADMIN)),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404, "Product not found")
    product.quantity += stock.quantity
    db.add(Transaction(
        product_id=product.id,
        user_id=current_user.id,
        transaction_type=TransactionType.STOCK_IN,
        quantity=stock.quantity,
    ))
    db.commit()
    db.refresh(product)
    return product