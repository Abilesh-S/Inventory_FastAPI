from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.product import Product
from app.models.transaction import Transaction, TransactionType
from app.models.user import User, RoleEnum
from app.schemas.transaction import TransactionCreate, TransactionOut
from app.core.dependencies import require_role
from app.services.audit_service import log_action

router = APIRouter(prefix="/employee", tags=["Employee"])

@router.post("/sell", response_model=TransactionOut)
def sell_stock(
    txn: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.EMPLOYEE, RoleEnum.ADMIN)),
):
    product = db.query(Product).filter(Product.id == txn.product_id).first()
    if not product:
        raise HTTPException(404, "Product not found")
    if product.quantity < txn.quantity:
        raise HTTPException(400, "Insufficient stock")

    product.quantity -= txn.quantity
    new_txn = Transaction(
        product_id=txn.product_id,
        user_id=current_user.id,
        customer_id=txn.customer_id,
        transaction_type=TransactionType.SALE,
        quantity=txn.quantity,
    )
    db.add(new_txn)

    log_action(
        db,
        user_id=current_user.id,
        action="STOCK_SOLD",
        details=f"product_id={txn.product_id}, quantity={txn.quantity}, customer_id={txn.customer_id}",
    )

    db.commit()
    db.refresh(new_txn)
    return new_txn