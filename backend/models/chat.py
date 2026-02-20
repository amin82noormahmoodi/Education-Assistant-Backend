import uuid
from sqlalchemy import Column, Integer, String, DateTime, Text, func
from core.db import Base


class ChatSession(Base):
    __tablename__ = "chat_session"
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(
        String(36),
        unique=True,
        index=True,
        nullable=False,
        default=lambda: str(uuid.uuid4()),
    )
    user_uuid = Column(String(36), index=True, nullable=False)
    title = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ChatMessage(Base):
    __tablename__ = "chat_message"
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(String(36), index=True, nullable=False)
    user_uuid = Column(String(36), index=True, nullable=False)
    role = Column(String(10), nullable=False)  # user / assistant
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())