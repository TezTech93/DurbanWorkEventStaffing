from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from auth import get_current_user, get_db
from models import User
from schemas import JobCreate, JobOut, BookingCreate, BookingOut, MessageCreate, MessageOut, UserOut
from Clients.manager import ClientManager
from schemas import PaymentIntentCreate, PaymentIntentResponse

router = APIRouter()

@router.post("/jobs", response_model=JobOut)
def create_job(
    job: JobCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "client":
        raise HTTPException(status_code=403, detail="Only clients can create jobs")
    return ClientManager.create_job(db, current_user.id, job)

@router.post("/book", response_model=BookingOut)
def book_event(
    booking: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "client":
        raise HTTPException(status_code=403, detail="Only clients can book")
    return ClientManager.book_event(db, current_user.id, booking)

@router.get("/employees", response_model=list[UserOut])
def view_employees(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "client":
        raise HTTPException(status_code=403, detail="Only clients can view employees")
    return ClientManager.view_employee_profiles(db)

@router.post("/messages", response_model=MessageOut)
def send_message(
    msg: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Clients can send messages to anyone (employees or other clients)
    return ClientManager.send_message(db, current_user.id, msg)

# Optionally add endpoints to view client's own jobs/bookings