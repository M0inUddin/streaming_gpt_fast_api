import asyncio

from typing import List

from models.messages import Message
from models.chat_sessions import ChatSession

from uuid import uuid4

from sqlalchemy.orm import Session

from database.db import get_db

from fastapi import APIRouter, HTTPException, Depends

from sse_starlette.sse import EventSourceResponse

from services.llm import prompt_llm_async
from services.llm import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam, ChatCompletionAssistantMessageParam, ChatCompletionToolMessageParam, ChatCompletionFunctionMessageParam

chat_router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)

@chat_router.post("/send/{session_id}")
async def send_message(session_id: str, user_message: str, db: Session = Depends(get_db)) -> dict:
    chat_session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not chat_session:
        raise HTTPException(status_code=404, detail="Session not found")

    existing_messages = db.query(Message).filter(Message.session_id == session_id).all()

    # Converting the existing messages to the format required by the LLM
    existing_messages_typed: List[ChatCompletionSystemMessageParam | ChatCompletionUserMessageParam | ChatCompletionAssistantMessageParam | ChatCompletionToolMessageParam | ChatCompletionFunctionMessageParam] = [
        ChatCompletionUserMessageParam(content=str(message.content), role="user") for message in existing_messages
    ]

    ai_response_stream = await prompt_llm_async(user_message_content=user_message, existing_messages=existing_messages_typed)

    # Processing the AI response and storing it in the DB
    for chunk in ai_response_stream:
        ai_message = chunk.choices[0].delta.content
        new_ai_message = Message(
            message_id=str(uuid4()),
            session_id=session_id,
            message_type="ai",
            content=ai_message
        )
        db.add(new_ai_message)
        db.commit()

    return {"message": "Message sent successfully"}

@chat_router.get("/receive/{session_id}")
async def receive_response(session_id: str, db: Session = Depends(get_db)) -> EventSourceResponse:
    async def event_generator():
        last_message_id = 0  # Initializing with a default value that ensures all messages are selected initially
        while True:
            # Query for new messages since the last message ID
            query = db.query(Message).filter(Message.session_id == session_id)
            if last_message_id:
                query = query.filter(Message.message_id > last_message_id)
            
            new_messages = query.order_by(Message.message_id).all()

            for message in new_messages:
                print(f"Yielding message: {message.content}")
                yield {"data": message.content}
                last_message_id = message.message_id

            # Wait before checking for new messages again
            await asyncio.sleep(1)

    return EventSourceResponse(event_generator())
