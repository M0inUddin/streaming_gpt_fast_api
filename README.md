# SWE, Backend & Applied ML take-home assignment

This project demonstrates a back-end engineering solution incorporating tools and technologies essential in modern software development. The project focuses on a Chat Service, leveraging OpenAI's Python SDK to interact with GPT, FastAPI for web framework, and Pydantic for data management. It simulates a real-world application and aims to provide insights into day-to-day work in a similar role.

## Project Overview

The Chat Service is a barebones chat application designed to facilitate interaction between users and an AI, powered by OpenAI's GPT-4. The service is built using FastAPI and utilizes Server-Sent Events (SSEs) for streaming data. The primary features of the service include:

- **Creation of Chat Sessions:** Users can initiate new chat sessions.
- **Sending and Receiving Messages:** Within a chat session, users can send messages and receive AI responses in real-time.
- **Streaming AI Responses:** AI responses are streamed using SSEs, enhancing the user experience with real-time interaction.
- **Message History Retrieval:** Users can fetch the complete history of messages exchanged in a given chat session.

## Technical Implementation

### FastAPI Application

- **Main.py:** The FastAPI app, including routes for chat session management and message handling.

#### Routes

- **POST /api/create_session:** Creates a new chat session.
- **POST /api/chat/send/{session_id}:** Sends a user message to the specified session and awaits AI response.
- **GET /api/chat/receive/{session_id}:** Streams AI responses using SSE.
- **GET /api/history/{session_id}:** Retrieves the entire message history for a session.

## Large Language Model (LLM) Integration

- LLM.py: Code for synchronous and asynchronous prompting of the LLM.
- OpenAI Chat Completions API: Used for generating AI responses to user messages.

## Persistence

- **In-Memory Storage:** Chat messages are stored in memory. Using SQLite

## Running the Service

- **Local Server:** Run using uvicorn main:app --reload.
- **LLM Interaction:** Test LLM responses using python llm.py "message".
