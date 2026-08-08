from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from models import UserRole, JobStatus, BookingStatus

# ---------- Auth ----------
class UserRegister(BaseModel):
    username: str
    password: str
    full_name: str
    role: UserRole
    # optional employee fields
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# ---------- Users ----------
class UserOut(BaseModel):
    id: int
    username: str
    full_name: str
    role: UserRole
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    bio: Optional[str] = None

    class Config:
        orm_mode = True

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

# ---------- Jobs ----------
class JobCreate(BaseModel):
    title: str
    description: str
    latitude: float
    longitude: float
    fee: float
    deposit_percent: Optional[float] = 25.0

class JobOut(BaseModel):
    id: int
    title: str
    description: str
    latitude: float
    longitude: float
    fee: float
    deposit_percent: float
    status: JobStatus
    client_id: int
    employee_id: Optional[int] = None
    created_at: datetime
    client: Optional[UserOut] = None
    employee: Optional[UserOut] = None

    class Config:
        orm_mode = True

# ---------- Bookings ----------
class BookingCreate(BaseModel):
    job_id: int
    employee_id: int

class BookingOut(BaseModel):
    id: int
    job_id: int
    employee_id: int
    status: BookingStatus
    deposit_paid: float
    booked_at: datetime

    class Config:
        orm_mode = True

# ---------- Messages ----------
class MessageCreate(BaseModel):
    receiver_id: int
    content: str

class MessageOut(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    content: str
    timestamp: datetime

    class Config:
        orm_mode = True

# ---------- Resume ----------
class ResumeOut(BaseModel):
    id: int
    employee_id: int
    filename: str
    uploaded_at: datetime

class PaymentIntentCreate(BaseModel):
    job_id: int

class PaymentIntentResponse(BaseModel):
    client_secret: str
    payment_intent_id: str
    amount: float
    currency: str = "usd"