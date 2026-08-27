from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog

def log_action(db: Session, user_id: int, action: str, details: str = None):
    """
    Writes an audit entry. Doesn't commit itself — call this right before
    the route's own db.commit() so both the operation and its audit log
    land in the same transaction (if one fails, both roll back together).
    """
    entry = AuditLog(user_id=user_id, action=action, details=details)
    db.add(entry)