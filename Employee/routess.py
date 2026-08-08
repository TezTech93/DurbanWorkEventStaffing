from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from auth import get_current_user, get_db
from models import User
from schemas import JobOut, BookingOut, MessageCreate, MessageOut, UserOut, UserProfileUpdate
from Employee.manager import EmployeeManager

router = APIRouter()

@router.get("/jobs", response_model=list[JobOut])
def view_jobs(
    radius: float = 25,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "employee":
        raise HTTPException(status_code=403, detail="Only employees can view jobs")
    return EmployeeManager.view_jobs_within_radius(db, current_user.id, radius)

@router.post("/jobs/{job_id}/accept", response_model=BookingOut)
def accept_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "employee":
        raise HTTPException(status_code=403, detail="Only employees can accept jobs")
    return EmployeeManager.accept_job(db, current_user.id, job_id)

@router.post("/jobs/{job_id}/deny", response_model=BookingOut)
def deny_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "employee":
        raise HTTPException(status_code=403, detail="Only employees can deny jobs")
    return EmployeeManager.deny_job(db, current_user.id, job_id)

@router.post("/messages", response_model=MessageOut)
def send_message(
    msg: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return EmployeeManager.send_message(db, current_user.id, msg)

@router.post("/resume")
def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "employee":
        raise HTTPException(status_code=403, detail="Only employees can upload resumes")
    return EmployeeManager.upload_resume(db, current_user.id, file)

@router.get("/profile", response_model=UserOut)
def view_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "employee":
        raise HTTPException(status_code=403, detail="Only employees can view their profile")
    return EmployeeManager.view_profile(db, current_user.id)

@router.put("/profile", response_model=UserOut)
def update_profile(
    update: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "employee":
        raise HTTPException(status_code=403, detail="Only employees can update their profile")
    return EmployeeManager.update_profile(db, current_user.id, update)