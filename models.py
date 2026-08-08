from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from database import Base

class UserRole(str, enum.Enum):
    client = "client"
    employee = "employee"

class JobStatus(str, enum.Enum):
    open = "open"
    booked = "booked"
    completed = "completed"

class BookingStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    denied = "denied"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    role = Column(Enum(UserRole))
    # employee‑specific fields
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    bio = Column(Text, nullable=True)

    jobs_created = relationship("Job", foreign_keys="Job.client_id", back_populates="client")
    jobs_assigned = relationship("Job", foreign_keys="Job.employee_id", back_populates="employee")
    bookings = relationship("Booking", back_populates="employee")
    messages_sent = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender")
    messages_received = relationship("Message", foreign_keys="Message.receiver_id", back_populates="receiver")
    resume = relationship("Resume", back_populates="employee", uselist=False)

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    latitude = Column(Float)
    longitude = Column(Float)
    fee = Column(Float)                 # total fee
    deposit_percent = Column(Float, default=25.0)  # deposit percentage
    status = Column(Enum(JobStatus), default=JobStatus.open)
    client_id = Column(Integer, ForeignKey("users.id"))
    employee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    client = relationship("User", foreign_keys=[client_id], back_populates="jobs_created")
    employee = relationship("User", foreign_keys=[employee_id], back_populates="jobs_assigned")
    bookings = relationship("Booking", back_populates="job")

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    employee_id = Column(Integer, ForeignKey("users.id"))
    status = Column(Enum(BookingStatus), default=BookingStatus.pending)
    deposit_paid = Column(Float, default=0.0)
    booked_at = Column(DateTime, default=datetime.utcnow)

    job = relationship("Job", back_populates="bookings")
    employee = relationship("User", back_populates="bookings")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

    sender = relationship("User", foreign_keys=[sender_id], back_populates="messages_sent")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="messages_received")

class Resume(Base):
    __tablename__ = "resumes"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("users.id"), unique=True)
    filename = Column(String)
    filepath = Column(String)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    employee = relationship("User", back_populates="resume")