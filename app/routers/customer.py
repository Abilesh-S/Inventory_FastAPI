from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.product import Product
from app.models.transaction import Transaction, TransactionType
from app.schemas.transaction import TransactionCreate, TransactionOut

router = APIRouter(prefix="/customer", tags=["Customer"])

@router.post("/buy", response_model=TransactionOut)
def buy_stock(txn: TransactionCreate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == txn.product_id).first()
    if not product:
        raise HTTPException(404, "Product not found")
    if product.quantity < txn.quantity:
        raise HTTPException(400, "Insufficient stock")
    product.quantity -= txn.quantity
    new_txn = Transaction(product_id=txn.product_id, user_id=txn.user_id,
                          transaction_type=TransactionType.PURCHASE, quantity=txn.quantity)
    db.add(new_txn)
    db.commit()
    db.refresh(new_txn)
    return new_txn