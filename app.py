from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from Clients.routes import router as client_router
from Employee.routess import router as employee_router
from auth_routes import router as auth_router
from webhooks import router as webhook_router

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Crew Booking API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(client_router, prefix="/client", tags=["client"])
app.include_router(employee_router, prefix="/employee", tags=["employee"])
app.include_router(webhook_router, prefix="/webhooks", tags=["webhooks"])

@app.get("/")
def root():
    return {"message": "Crew Booking API"}