from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db.database import get_db
from app.models.product import Product
from app.models.transaction import Transaction, TransactionType
from app.models.user import User, RoleEnum
from app.schemas.product import ProductCreate, ProductOut, StockUpdate , ProductBase
from app.core.dependencies import require_role
from app.services.audit_service import log_action
from app.core.logger import logger

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/products", response_model=ProductOut)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.ADMIN)),
):
    logger.info(f"create_product called by user_id={current_user.id}, sku={product.sku}")

    if db.query(Product).filter(Product.sku == product.sku).first():
        logger.warning(f"create_product failed - duplicate sku={product.sku}")
        raise HTTPException(400, "SKU already exists")

    new_product = Product(**product.dict())
    db.add(new_product)
    db.flush()

    log_action(
        db,
        user_id=current_user.id,
        action="PRODUCT_CREATED",
        details=f"product_id={new_product.id}, sku={new_product.sku}, name={new_product.name}",
    )

    db.commit()
    db.refresh(new_product)
    logger.info(f"create_product success - product_id={new_product.id}")
    return new_product


@router.post("/products/{product_id}/add-stock", response_model=ProductOut)
def add_stock(
    product_id: int,
    stock: StockUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.ADMIN)),
):
    logger.info(f"add_stock called by user_id={current_user.id}, product_id={product_id}, quantity={stock.quantity}")

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        logger.warning(f"add_stock failed - product_id={product_id} not found")
        raise HTTPException(404, "Product not found")

    product.quantity += stock.quantity
    db.add(Transaction(
        product_id=product.id,
        user_id=current_user.id,
        transaction_type=TransactionType.STOCK_IN,
        quantity=stock.quantity,
    ))

    log_action(
        db,
        user_id=current_user.id,
        action="STOCK_ADDED",
        details=f"product_id={product.id}, quantity={stock.quantity}, new_total={product.quantity}",
    )

    db.commit()
    db.refresh(product)
    logger.info(f"add_stock success - product_id={product.id}, new_total={product.quantity}")
    return product


@router.get("/products", response_model=List[ProductOut])
def list_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.ADMIN, RoleEnum.EMPLOYEE)),
):
    logger.info(f"list_products called by user_id={current_user.id}")
    return db.query(Product).all()


@router.delete("/products/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.ADMIN)),
):
    logger.info(f"delete_product called by user_id={current_user.id}, product_id={product_id}")

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        logger.warning(f"delete_product failed - product_id={product_id} not found")
        raise HTTPException(404, "Product not found")

    log_action(
        db,
        user_id=current_user.id,
        action="PRODUCT_DELETED",
        details=f"product_id={product.id}, sku={product.sku}, name={product.name}",
    )

    try:
        db.delete(product)
        db.commit()
    except IntegrityError:
        db.rollback()
        logger.error(f"delete_product failed - product_id={product_id} has transaction history")
        raise HTTPException(
            400,
            "Cannot delete product — it already has transaction history. Consider marking it inactive instead.",
        )

    logger.info(f"delete_product success - product_id={product_id}")
    return {"detail": f"Product '{product.name}' deleted successfully"}

@router.put("/products/{productid}", response_model=ProductOut)
def update_product(
    productid: int,
    product: ProductBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.ADMIN)),
):
    existProduct = db.query(Product).filter(Product.id == productid).first()
    if not existProduct:
        raise HTTPException(404, "Product not found")

    existProduct.name = product.name
    existProduct.sku = product.sku
    existProduct.price = product.price

    db.commit()
    db.refresh(existProduct)
    return existProduct