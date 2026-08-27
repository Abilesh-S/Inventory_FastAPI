from fastapi import FastAPI
from app.db.database import engine
from app.db.base import Base
from app.routers import admin, employee, customer, auth

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Inventory Management System")
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(employee.router)
app.include_router(customer.router)

@app.get("/")
def root():
    return {"message": "Inventory API running"}