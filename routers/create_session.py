from fastapi import APIRouter, Depends

from models.chat_sessions import ChatSession

from uuid import uuid4

from sqlalchemy.orm import Session

from database.db import get_db

create_session_router = APIRouter(
    prefix="/create_session",
    tags=["create_session"],
)

@create_session_router.post("/")
def create_session(db: Session = Depends(get_db)) -> dict:
    new_session = ChatSession(session_id=str(uuid4()))
    db.add(new_session)
    db.commit()
    return {"session_id": new_session.session_id}
