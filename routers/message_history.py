from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from database.db import get_db

from models.messages import Message

get_history_router = APIRouter(
    prefix="/history",
    tags=["history"],
)

@get_history_router.get("/{session_id}")
def get_history(session_id: str, db: Session = Depends(get_db)) -> dict:
    messages = db.query(Message).filter(Message.session_id == session_id).all()
    if not messages:
        raise HTTPException(status_code=404, detail="No messages found for this session")

    return {"messages": [message.content for message in messages]}
