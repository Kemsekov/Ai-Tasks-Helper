# AI Task Manager

An intelligent task management system that uses AI to automatically analyze and categorize tasks.

## Features

- Add tasks in natural language
- AI-powered task classification (priority, category, estimated time)
- Subtask generation
- Provider-agnostic AI integration (supports OpenRouter, OpenAI, Anthropic, etc.)
- Dynamic provider, token, and model configuration via web UI
- Real-time token and model validation
- RESTful API for task management
- User-specific task organization
- PostgreSQL database storage
- Web-based frontend with intuitive UI
- Docker containerization for easy deployment

## Tech Stack

- Python 3.10+
- FastAPI (Backend API)
- Flask (Frontend Server)
- PostgreSQL
- OpenAI-compatible APIs (OpenRouter, OpenAI, Anthropic, etc.)
- Docker & Docker Compose
- HTML/CSS/JavaScript (Frontend)

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
POSTGRES_HOST=postgres_db
POSTGRES_PORT=5432

# Backend settings
BACKEND_CONTAINER_NAME="ai_task_helper_back"
BACKEND_INTERNAL_HOST="0.0.0.0"
BACKEND_INTERNAL_PORT=8000
BACKEND_PORT=8001
BACKEND_SECRET=super-secret
BACKEND_DEBUG=True
```

**Note**: Unlike previous versions, AI provider settings (token, model, provider URL) are now configured dynamically through the web interface rather than environment variables.

## Services

The application consists of three main services:
- **PostgreSQL**: Database storage
- **Backend**: FastAPI server with AI integration
- **Frontend**: Flask server with web interface

## API Endpoints

### Backend API (available at http://localhost:8001/)
- `GET /health` - Check if the backend is running
- `GET /api/config` - Get the current AI configuration (provider URL, model, token status)
- `POST /api/update-config` - Update the AI configuration (provider URL, token, model)
- `GET /api/health` - Check if the AI provider API token is valid with specified model
- `POST /api/v1/tasks/` - Create a new task (AI will classify it)
- `GET /api/v1/tasks/{task_id}` - Get a specific task
- `GET /api/v1/users/{user_id}/tasks` - Get all tasks for a user
- `PUT /api/v1/tasks/{task_id}` - Update a task
- `DELETE /api/v1/tasks/{task_id}` - Delete a task

### Frontend API (available at http://localhost:5000/api/)
- `GET /health` - Check backend health status
- `GET /config` - Get current AI configuration
- `POST /update-config` - Update AI configuration (provider URL, token, model)
- `GET /model` - Get current AI model
- `POST /update-model` - Update AI model
- `POST /tasks/` - Create a new task
- `GET /users/{user_id}/tasks` - Get all tasks for a user

## Web Interface

Access the user-friendly web interface at `http://localhost:5000` to:
- View and manage tasks with a clean UI
- Configure your AI provider settings (URL, token, model) in real-time
- Validate provider credentials
- Monitor provider status
- Add, view, update, and delete tasks

## Usage

After starting the service, access the web interface at `http://localhost:5000` to manage your tasks.

On the web interface, you can:
1. Enter your AI provider URL (e.g., https://openrouter.ai/api/v1, https://api.openai.com/v1)
2. Enter your API token for the provider
3. Select or enter the model name to use (e.g., openai/gpt-4, anthropic/claude-3-haiku, qwen/qwen3-coder:free)
4. Validate your settings
5. Start managing tasks with AI classification

Example task creation:
```json
{
  "title": "Prepare presentation for team meeting",
  "description": "Create slides covering quarterly results and upcoming initiatives",
  "user_id": "user123"
}
```

The AI will automatically classify the task with priority, category, estimated time, and potential subtasks based on your configured provider settings.