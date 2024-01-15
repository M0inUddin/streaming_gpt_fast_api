"""Main project file"""

import asyncio
import random

from fastapi import FastAPI
from fastapi.openapi.models import Info

from routers.chat import chat_router
from routers.create_session import create_session_router
from routers.message_history import get_history_router

from sse_starlette.sse import EventSourceResponse

from models.messages import Base as MessagesBase
from models.chat_sessions import Base as ChatSessionsBase

from database.db import engine

# Initilizing the DB
MessagesBase.metadata.create_all(bind=engine)
ChatSessionsBase.metadata.create_all(bind=engine)

# Giving the app some metadata
app = FastAPI(
    title="FastAPI App",
    description="This is a simple API built with FastAPI for the purpose of demonstrating how to stream data to a client using Server-Sent Events (SSEs).",
    version="1.0.0",
    openapi_info=Info(
        title="FastAPI App",
        description="This is a simple API built with FastAPI for the purpose of demonstrating how to stream data to a client using Server-Sent Events (SSEs).",
        version="1.0.0"
    )
)

# Including the routers context to the app
app.include_router(create_session_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(get_history_router, prefix="/api")

@app.get("/stream-example")
async def stream_example():
    """
    Example route for streaming text to the client, one word/token at a time.
    """
    async def stream_tokens():
        """
        Placeholder implementation for token streaming. Try running this route as-is to better understand how to
        stream data using Server-Sent Events (SSEs) in FastAPI.
        See this tutorial for more information: https://devdojo.com/bobbyiliev/how-to-use-server-sent-events-sse-with-fastapi
        """
        for token in ['hello', ', ', 'this ', 'is ', 'a ', 'streamed ', 'response.']:
            # fake delay:
            await asyncio.sleep(random.randint(0, 3))

            print(f"Yielding token: {token}")
            yield token

    return EventSourceResponse(stream_tokens())

