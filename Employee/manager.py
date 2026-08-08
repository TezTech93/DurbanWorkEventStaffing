from sqlalchemy.orm import Session
from models import User, Job, Booking, Message, Resume
from schema import MessageCreate
from utils import haversine
from fastapi import HTTPException, status, UploadFile
import os
import shutil

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class EmployeeManager:
    @staticmethod
    def view_jobs_within_radius(db: Session, employee_id: int, radius_miles: float = 25):
        employee = db.query(User).filter(User.id == employee_id).first()
        if not employee or employee.latitude is None or employee.longitude is None:
            raise HTTPException(status_code=400, detail="Employee location not set")
        all_jobs = db.query(Job).filter(Job.status == "open").all()
        nearby = []
        for job in all_jobs:
            dist = haversine(employee.latitude, employee.longitude, job.latitude, job.longitude)
            if dist <= radius_miles:
                nearby.append(job)
        return nearby

    @staticmethod
    def accept_job(db: Session, employee_id: int, job_id: int):
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        if job.status != "open":
            raise HTTPException(status_code=400, detail="Job not available")
        # Check if employee already has a booking for this job
        existing = db.query(Booking).filter(Booking.job_id == job_id, Booking.employee_id == employee_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Already booked or applied")
        # Create a booking with accepted status directly? Or create pending and then accept?
        # According to notes "accept/deny job" – we assume employee accepts a job offer (which implies a booking exists?)
        # We'll simplify: accept creates a booking with status 'accepted' and updates job status to 'booked'
        booking = Booking(
            job_id=job_id,
            employee_id=employee_id,
            status="accepted",
            deposit_paid=job.fee * (job.deposit_percent / 100.0)
        )
        job.status = "booked"
        job.employee_id = employee_id
        db.add(booking)
        db.commit()
        db.refresh(booking)
        return booking

    @staticmethod
    def deny_job(db: Session, employee_id: int, job_id: int):
        # Similar: deny an open job? Or deny a pending booking? We'll handle denial of a pending booking.
        booking = db.query(Booking).filter(Booking.job_id == job_id, Booking.employee_id == employee_id).first()
        if not booking:
            raise HTTPException(status_code=404, detail="No booking found")
        if booking.status != "pending":
            raise HTTPException(status_code=400, detail="Booking already processed")
        booking.status = "denied"
        db.commit()
        db.refresh(booking)
        return booking

    @staticmethod
    def send_message(db: Session, sender_id: int, msg: MessageCreate):
        receiver = db.query(User).filter(User.id == msg.receiver_id).first()
        if not receiver:
            raise HTTPException(status_code=404, detail="Receiver not found")
        message = Message(
            sender_id=sender_id,
            receiver_id=msg.receiver_id,
            content=msg.content
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        return message

    @staticmethod
    def upload_resume(db: Session, employee_id: int, file: UploadFile):
        # Check if employee already has resume
        existing = db.query(Resume).filter(Resume.employee_id == employee_id).first()
        if existing:
            # Optionally delete old file
            if os.path.exists(existing.filepath):
                os.remove(existing.filepath)
            db.delete(existing)
            db.commit()
        # Save new file
        filename = f"{employee_id}_{file.filename}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        resume = Resume(
            employee_id=employee_id,
            filename=file.filename,
            filepath=filepath
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)
        return resume

    @staticmethod
    def view_profile(db: Session, employee_id: int):
        employee = db.query(User).filter(User.id == employee_id).first()
        return employee

    @staticmethod
    def update_profile(db: Session, employee_id: int, update_data):
        employee = db.query(User).filter(User.id == employee_id).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        for key, value in update_data.dict(exclude_unset=True).items():
            setattr(employee, key, value)
        db.commit()
        db.refresh(employee)
        return employee