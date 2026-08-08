# webhooks.py (or inside app.py)

from fastapi import APIRouter, Request, HTTPException
from stripe_config import stripe, STRIPE_WEBHOOK_SECRET
from database import SessionLocal
from models import Job, Booking
import stripe

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

@router.post("/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    if not STRIPE_WEBHOOK_SECRET:
        raise HTTPException(400, "Webhook secret not configured")
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(400, "Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(400, "Invalid signature")

    # Handle the event
    if event["type"] == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        # Update job/booking status
        job_id = payment_intent["metadata"].get("job_id")
        if job_id:
            db = SessionLocal()
            job = db.query(Job).filter(Job.id == int(job_id)).first()
            if job:
                # Optionally mark job as booked (if deposit confirms booking)
                job.status = "booked"
                # Also create a booking record if not already created
                # You may already have a booking record from the "book" endpoint.
                db.commit()
            db.close()
    return {"status": "success"}