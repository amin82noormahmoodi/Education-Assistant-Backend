from sqlalchemy import Column, Integer, String, DateTime, func
from core.db import Base


class PendingUser(Base):
    __tablename__ = "pending_user"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(36), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    otp_code = Column(String(10), nullable=False)
    otp_expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


