# Conversation Service REST API

A FastAPI-based REST API for the ConversationService supporting multiple agent types.

## Features

- RESTful API for managing conversations with different agent types
- OAuth2 Bearer token authentication (token is user_id for demo)
- Multiple agent types (MathSemanticKernelAgent, MathLlamaIndexAgent, DefectsAnalysisAgent)
- Pagination and filtering for conversations
- CRUD operations for conversations

## API Endpoints

| Method | Endpoint                                  | Description                                   |
| ------ | ----------------------------------------- | --------------------------------------------- |
| GET    | /                                         | Check if the API is running                   |
| GET    | /agents                                   | List all available agents                     |
| POST   | /conversations                            | Create a new conversation                     |
| GET    | /conversations                            | List conversations for the authenticated user |
| GET    | /conversations/{conversation_id}          | Get a conversation by ID                      |
| POST   | /conversations/{conversation_id}/messages | Send a message in a conversation              |
| POST   | /conversations/{conversation_id}/reset    | Reset a conversation (clear message history)  |
| DELETE | /conversations/{conversation_id}          | Delete a conversation                         |

## Getting Started

### Prerequisites

- Python 3.10+
- FastAPI, Uvicorn

### Installation & Run

```bash
poetry lock --no-update
poetry install --with chatbot
poetry run python main.py
```

API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## Authentication

OAuth2 Bearer token is required. For demo, the token is used as user_id directly.

Example:

```bash
curl -X GET "http://localhost:8000/conversations" \
     -H "Authorization: Bearer user123"
```

## Usage Examples

Create a Conversation:

```bash
curl -X POST "http://localhost:8000/conversations" \
     -H "Authorization: Bearer user123" \
     -H "Content-Type: application/json" \
     -d '{"agent_id": "math_semantic_kernel_agent", "title": "Math Problems"}'
```

Send a Message:

```bash
curl -X POST "http://localhost:8000/conversations/YOUR_CONVERSATION_ID/messages" \
     -H "Authorization: Bearer user123" \
     -H "Content-Type: application/json" \
     -d '{"content": "What is 15 * 7?"}'
```

## Client Library

A Python client is included (see `client.py`) for easy API interaction.
