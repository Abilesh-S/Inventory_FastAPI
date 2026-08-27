from sqlalchemy.orm import declarative_base

Base = declarative_base()

from app.models import user, product, transaction, customer, audit_log  # noqa: E402,F401