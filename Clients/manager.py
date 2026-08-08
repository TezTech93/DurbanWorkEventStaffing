from sqlalchemy.orm import Session
from models import User, Job, Booking, Message
from schema import JobCreate, BookingCreate, MessageCreate
from fastapi import HTTPException, status
import stripe
from stripe_config import stripe  # or import stripe


class ClientManager:
    @staticmethod
    def create_job(db: Session, client_id: int, job_data: JobCreate):
        job = Job(
            **job_data.dict(),
            client_id=client_id,
            status="open"
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def book_event(db: Session, client_id: int, booking_data: BookingCreate):
        # Check if job exists and is open
        job = db.query(Job).filter(Job.id == booking_data.job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        if job.status != "open":
            raise HTTPException(status_code=400, detail="Job is not open")
        # Ensure the client owns the job
        if job.client_id != client_id:
            raise HTTPException(status_code=403, detail="Not your job")
        # Check employee exists
        employee = db.query(User).filter(User.id == booking_data.employee_id, User.role == "employee").first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        # Calculate deposit
        deposit = job.fee * (job.deposit_percent / 100.0)
        booking = Booking(
            job_id=job.id,
            employee_id=employee.id,
            deposit_paid=deposit,
            status="pending"
        )
        # Optionally update job status to 'booked' after booking accepted? We'll keep as open until accepted.
        db.add(booking)
        db.commit()
        db.refresh(booking)
        return booking

    @staticmethod
    def view_employee_profiles(db: Session):
        employees = db.query(User).filter(User.role == "employee").all()
        return employees

    @staticmethod
    def send_message(db: Session, sender_id: int, msg: MessageCreate):
        # Check receiver exists
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
    def create_payment_intent(db: Session, client_id: int, job_id: int):
        job = db.query(Job).filter(Job.id == job_id, Job.client_id == client_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        if job.status != "open":
            raise HTTPException(status_code=400, detail="Job is not open for booking")
        # Calculate deposit amount (in cents for Stripe)
        deposit_amount = int(job.fee * (job.deposit_percent / 100.0) * 100)  # in cents
        # Create PaymentIntent
        intent = stripe.PaymentIntent.create(
            amount=deposit_amount,
            currency="usd",
            metadata={"job_id": job.id, "client_id": client_id},
            # You can add a description
        )
        # Save intent ID to job (optional but useful)
        job.stripe_payment_intent_id = intent.id
        db.commit()
        return intent.client_secret, intent.id, deposit_amount / 100.0