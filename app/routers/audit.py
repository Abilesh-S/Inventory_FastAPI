from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.audit_log import AuditLog
from app.models.user import User, RoleEnum
from app.schemas.audit_log import AuditLogOut
from app.core.dependencies import require_role
from app.core.logger import logger

router = APIRouter(prefix="/audit", tags=["Audit"])

@router.get("/", response_model=List[AuditLogOut])
def get_audit_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.ADMIN)),
):
    logger.info(f"get_audit_logs called by user_id={current_user.id}")
    return db.query(AuditLog).order_by(AuditLog.timestamp.desc()).all()