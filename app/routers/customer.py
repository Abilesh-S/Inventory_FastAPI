from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.customer import Customer
from app.models.user import User, RoleEnum
from app.schemas.customer import CustomerCreate, CustomerOut
from app.core.dependencies import require_role

router = APIRouter(prefix="/customers", tags=["Customer"])

@router.post("/", response_model=CustomerOut)
def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.ADMIN, RoleEnum.EMPLOYEE)),
):
    new_customer = Customer(**customer.dict())
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer

@router.get("/{customer_id}", response_model=CustomerOut)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.ADMIN, RoleEnum.EMPLOYEE)),
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(404, "Customer not found")
    return customer