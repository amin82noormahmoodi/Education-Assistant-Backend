import os
import tempfile
from pathlib import Path
from pydub import AudioSegment

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session

from utils.agentic_system_module import agentic_system
from utils.title_generator_module import generate_title
from utils.asr_module import transcribe_audio_google
from schemas.chat import ChatStart, ChatResponse, ChatAsk, ChatTitleRequest
from models import User, ChatSession, ChatMessage
from core.db import SessionLocal 

router = APIRouter(prefix="/chat", tags=["chat"])

CONTENT_TYPE_EXTENSION = {
    "audio/wav": ".wav",
    "audio/x-wav": ".wav",
    "audio/mp3": ".mp3",
    "audio/mpeg": ".mp3",
    "audio/ogg": ".ogg",
    "audio/webm": ".webm",
}

def convert_to_wav(source_path: str) -> str:
    audio = AudioSegment.from_file(source_path)
    wav_path = f"{source_path}.wav"
    audio.export(wav_path, format="wav")
    return wav_path

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/asr")
async def asr(file: UploadFile = File(...), language: str = "fa-IR"):
    if file.content_type not in CONTENT_TYPE_EXTENSION:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    tmp_files = []
    try:
        suffix = CONTENT_TYPE_EXTENSION.get(file.content_type) or Path(file.filename or "").suffix or ".dat"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_files.append(tmp.name)
            source_path = tmp.name
        wav_path = source_path
        if file.content_type not in {"audio/wav", "audio/x-wav"}:
            wav_path = convert_to_wav(source_path)
            tmp_files.append(wav_path)
        text = transcribe_audio_google(wav_path, language)
        return {"transcription" : text}
    
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        for path in tmp_files:
            if path and os.path.exists(path):
                os.remove(path)

@router.post("/ask", response_model=ChatResponse)
def ask(payload: ChatAsk, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.uuid == payload.user_uuid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    session = None
    if payload.chat_id:
        session = db.query(ChatSession).filter(
            ChatSession.chat_id == payload.chat_id,
            ChatSession.user_uuid == payload.user_uuid
        ).first()

    if not session:
        session = ChatSession(user_uuid=payload.user_uuid)
        db.add(session)
        db.commit()
        db.refresh(session)

    user_msg = ChatMessage(
        chat_id=session.chat_id,
        user_uuid=payload.user_uuid,
        role="user",
        content=payload.message,
    )
    db.add(user_msg)
    db.commit()

    if session.title is None:
        try:
            title = generate_title([{"role": "user", "content": payload.message}])
            session.title = title
            db.commit()
        except Exception:
            db.rollback()

    answer = agentic_system(payload.message)

    bot_msg = ChatMessage(
        chat_id=session.chat_id,
        user_uuid=payload.user_uuid,
        role="assistant",
        content=answer,
    )
    db.add(bot_msg)
    db.commit()

    return {"chat_id": session.chat_id, "answer": answer}


@router.post("/title")
def generate_chat_title(payload: ChatTitleRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.uuid == payload.user_uuid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    session = db.query(ChatSession).filter(
        ChatSession.chat_id == payload.chat_id,
        ChatSession.user_uuid == payload.user_uuid
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat not found")

    if session.title:
        return {"chat_id": session.chat_id, "title": session.title}

    title = generate_title([{"role": "user", "content": payload.message}])
    session.title = title
    db.commit()
    return {"chat_id": session.chat_id, "title": title}


@router.get("/sessions/{user_uuid}")
def list_sessions(user_uuid: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.uuid == user_uuid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    sessions = (
        db.query(ChatSession.chat_id)
        .filter(ChatSession.user_uuid == user_uuid)
        .order_by(ChatSession.created_at.desc())
        .all())
    return {"chat_ids": [row.chat_id for row in sessions]}


@router.get("/sessions/{user_uuid}/details")
def list_session_details(user_uuid: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.uuid == user_uuid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    sessions = (
        db.query(ChatSession)
        .filter(ChatSession.user_uuid == user_uuid)
        .order_by(ChatSession.created_at.desc())
        .all()
    )
    return {
        "sessions": [
            {
                "chat_id": session.chat_id,
                "title": session.title,
                "created_at": session.created_at,
            }
            for session in sessions
        ]
    }


@router.get("/messages/{user_uuid}/{chat_id}")
def get_messages(user_uuid: str, chat_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.uuid == user_uuid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    session = db.query(ChatSession).filter(
        ChatSession.chat_id == chat_id,
        ChatSession.user_uuid == user_uuid,
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat not found")

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.chat_id == chat_id, ChatMessage.user_uuid == user_uuid)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
    return {
        "chat_id": chat_id,
        "messages": [
            {
                "role": message.role,
                "content": message.content,
                "created_at": message.created_at,
            }
            for message in messages
        ],
    }