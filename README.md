# AI Task Manager

An intelligent task management system that uses AI to automatically analyze and categorize tasks.

## Features

- Add tasks in natural language
- AI-powered task classification (priority, category, estimated time)
- Subtask generation
- RESTful API for task management
- User-specific task organization
- PostgreSQL database storage

## Tech Stack

- Python 3.10+
- FastAPI
- PostgreSQL
- OpenRouter AI API
- Docker

## Setup

1. Clone the repository
2. Set up environment variables in `.env` file
3. Build and run with Docker Compose:

```bash
docker-compose up --build
```

## Environment Variables

The application requires the following environment variables in the `.env` file:

```env
# Database settings
POSTGRES_USER=webdev
POSTGRES_PASSWORD=webdev
POSTGRES_DB=webdev
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Backend settings
BACKEND_CONTAINER_NAME="ai_task_helper_back"
BACKEND_INTERNAL_HOST="0.0.0.0"
BACKEND_INTERNAL_PORT=8000
BACKEND_PORT=8001
BACKEND_SECRET=super-secret
BACKEND_DEBUG=True

# AI settings
OPENROUTER_TOKEN=your_openrouter_api_key_here
```

## API Endpoints

- `POST /api/v1/tasks/` - Create a new task (AI will classify it)
- `GET /api/v1/tasks/{task_id}` - Get a specific task
- `GET /api/v1/users/{user_id}/tasks` - Get all tasks for a user
- `PUT /api/v1/tasks/{task_id}` - Update a task
- `DELETE /api/v1/tasks/{task_id}` - Delete a task

## Usage

After starting the service, you can interact with the API directly or use the interactive documentation at `http://localhost:8001/docs`.

Example task creation:
```json
{
  "title": "Prepare presentation for team meeting",
  "description": "Create slides covering quarterly results and upcoming initiatives",
  "user_id": "user123"
}
```

The AI will automatically classify the task with priority, category, estimated time, and potential subtasks.