from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from core.db import SessionLocal
from core.security import (
    hash_password,
    verify_password,
    create_access_token,
    validate_password_length,
)
from models import User, PendingUser
from schemas import SignUpStart, VerifyOtp, SignIn, TokenResponse
from utils.otp_module import otp_sender

router = APIRouter(prefix="/auth", tags=["auth"])

OTP_EXPIRES_MINUTES = 2

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/signup/start")
def signup_start(payload: SignUpStart, db: Session = Depends(get_db)):
    if payload.password != payload.password_confirm:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    try:
        validate_password_length(payload.password)
    except ValueError:
        raise HTTPException(status_code=400, detail="Password too long")
    
    existing = db.query(User).filter(
        (User.student_id == payload.student_id) | (User.email == payload.email)
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Student ID or email already exists")
    pending = db.query(PendingUser).filter(
        (PendingUser.student_id == payload.student_id) | (PendingUser.email == payload.email)
    ).first()

    if pending and (pending.student_id != payload.student_id or pending.email != payload.email):
        raise HTTPException(status_code=400, detail="Student ID or email already exists")

    otp_code = otp_sender(payload.email)
    otp_expires = datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRES_MINUTES)

    if pending:
        pending.password_hash = hash_password(payload.password)
        pending.otp_code = otp_code
        pending.otp_expires_at = otp_expires
    else:
        pending = PendingUser(
            student_id=payload.student_id,
            email=payload.email,
            password_hash=hash_password(payload.password),
            otp_code=otp_code,
            otp_expires_at=otp_expires,
        )
        db.add(pending)

    db.commit()
    return {"message" : "OTP sent to email", "expires_in_minutes": OTP_EXPIRES_MINUTES}


@router.post("/signup/verify", response_model=TokenResponse)
def signup_verify(payload: VerifyOtp, db: Session = Depends(get_db)):
    pending = db.query(PendingUser).filter(PendingUser.student_id == payload.student_id).first()
    if not pending:
        raise HTTPException(status_code=404, detail="OTP not generated")
    if pending.otp_code != payload.otp_code:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    if datetime.now(timezone.utc) > pending.otp_expires_at:
        raise HTTPException(status_code=400, detail="OTP Expired")

    existing = db.query(User).filter(
        (User.student_id == pending.student_id) | (User.email == pending.email)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Student ID or email already exists")

    user = User(
        student_id=pending.student_id,
        email=pending.email,
        password_hash=pending.password_hash,
        is_verified=True,
    )
    db.add(user)
    db.delete(pending)
    db.commit()

    token = create_access_token(user.uuid)
    return {"access_token" : token, "user_uuid" : user.uuid}

@router.post("/signin", response_model=TokenResponse)
def siginin(payload: SignIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.student_id == payload.student_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credential")
    if not user.is_verified:
        raise HTTPException(status_code=401, detail="User not verified")
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid password")
    token = create_access_token(user.uuid)
    return {"access_token" : token, "user_uuid": user.uuid}

@router.delete("/users/{user_uuid}")
def delete_user(user_uuid: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.uuid == user_uuid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}