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

from database import engine, Base
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)

def add_missing_enum_values():
    """Add all possible values to the 'profession' enum, including both
    display names (e.g., 'Day Labor') and the frontend keys (e.g., 'day_labor').
    """
    # All possible values your frontend might send
    values_to_add = [
        # Display names (title case)
        'Day Labor', 'Construction Labor', 'General Labor',
        'Loading', 'Unloading', 'Warehouse Labor', 'Moving Help',
        'Hospitality', 'Event Staff', 'Cleanup Crew',
        'photographer', 'videographer',
        # Frontend key names (lowercase underscore)
        'day_labor', 'construction_labor', 'general_labor',
        'loading', 'unloading', 'warehouse_labor', 'moving_help',
        'hospitality', 'event_staff', 'cleanup_crew',
        'photographer', 'videographer'  # already present but safe
    ]

    try:
        with engine.connect() as conn:
            # Check if enum exists
            result = conn.execute(text("SELECT 1 FROM pg_type WHERE typname = 'profession'"))
            if result.scalar() is None:
                logging.info("Enum 'profession' does not exist yet – skipping.")
                return

            # Get existing labels
            existing = conn.execute(
                text("SELECT enumlabel FROM pg_enum WHERE enumtypid = 'profession'::regtype")
            ).fetchall()
            existing_labels = {row[0] for row in existing}

            # Add missing values
            added = 0
            for val in values_to_add:
                if val not in existing_labels:
                    logging.info(f"Adding enum value: {val}")
                    conn.execute(text(f"ALTER TYPE profession ADD VALUE '{val}'"))
                    added += 1
            conn.commit()
            if added:
                logging.info(f"Added {added} new enum values.")
            else:
                logging.info("All enum values already present.")
    except Exception as e:
        logging.error(f"Error while adding enum values: {e}")
    """Add all possible values to the 'profession' enum if they don't already exist."""
    values_to_add = [
        'Day Labor', 'Construction Labor', 'General Labor',
        'Loading', 'Unloading', 'Warehouse Labor', 'Moving Help',
        'Hospitality', 'Event Staff', 'Cleanup Crew',
        'photographer', 'videographer'
    ]

    try:
        with engine.connect() as conn:
            # Check if enum type exists
            result = conn.execute(text("SELECT 1 FROM pg_type WHERE typname = 'profession'"))
            if result.scalar() is None:
                logging.info("Enum 'profession' does not exist yet – skipping.")
                return

            # Get existing labels
            existing = conn.execute(
                text("SELECT enumlabel FROM pg_enum WHERE enumtypid = 'profession'::regtype")
            ).fetchall()
            existing_labels = {row[0] for row in existing}

            # Add missing values
            for val in values_to_add:
                if val not in existing_labels:
                    logging.info(f"Adding enum value: {val}")
                    conn.execute(text(f"ALTER TYPE profession ADD VALUE '{val}'"))
                    # Commit after each add (auto-commit is enabled? We'll commit at the end)
            conn.commit()
            logging.info("Enum values added successfully.")
    except Exception as e:
        logging.error(f"Error while adding enum values: {e}")

# --- Then later in app.py ---
Base.metadata.create_all(bind=engine)   # create tables if they don't exist
add_missing_enum_values()              # add missing enum values (runs after tables are created)