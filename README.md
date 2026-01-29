# AI Task Manager

An intelligent task management system that uses AI to automatically analyze and categorize tasks.

## Features

- Add tasks in natural language
- AI-powered task classification (priority, category, estimated time)
- Subtask generation
- Real-time AI token and model management
- Dynamic model switching (supports Qwen, Claude, OpenAI, and other models)
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
- OpenRouter AI API (supports OpenAI, Anthropic, Google, etc. compatible APIs)
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

# AI settings
OPENROUTER_TOKEN=your_openrouter_api_key_here
DEFAULT_MODEL="qwen/qwen3-coder:free"
```

## Services

The application consists of three main services:
- **PostgreSQL**: Database storage
- **Backend**: FastAPI server with AI integration
- **Frontend**: Flask server with web interface

## API Endpoints

### Backend API (available at http://localhost:8001/api/v1/)
- `POST /api/v1/tasks/` - Create a new task (requires provider_url, api_token, model_name query parameters, AI will classify it)
- `GET /api/v1/tasks/{task_id}` - Get a specific task
- `GET /api/v1/users/{user_id}/tasks` - Get all tasks for a user
- `PUT /api/v1/tasks/{task_id}` - Update a task
- `DELETE /api/v1/tasks/{task_id}` - Delete a task

### Backend Configuration Endpoints (available at http://localhost:8001/)
- `GET /health` - Check if backend is running
- `GET /api/config` - Get current AI configuration (provider URL, model, token)
- `POST /api/update-config` - Update AI configuration (provider URL, token, model)
- `GET /api/health` - Check if AI provider API token is valid with specified model

### Frontend API (available at http://localhost:5000/api/)
- `GET /health` - Check backend health status
- `GET /config` - Get current AI configuration
- `POST /update-config` - Update AI configuration (provider URL, token, model)
- `POST /tasks/` - Create a new task (forwards to backend with stored config)
- `GET /users/{user_id}/tasks` - Get all tasks for a user

## Web Interface

Access the user-friendly web interface at `http://localhost:5000` to:
- View and manage tasks with a clean UI
- Update your AI provider API token in real-time
- Switch between different AI models (Qwen, Claude, GPT, GLM, etc.)
- Validate provider credentials and model availability
- Monitor token and model status
- Add, view, update, and delete tasks

## Usage

After starting the service, access the web interface at `http://localhost:5000` to manage your tasks.

From the web interface, you can:
1. Configure your AI provider settings (URL, token, model)
2. Validate your configuration
3. Add tasks in natural language
4. View, update, and delete your tasks

Alternatively, you can interact with the API directly or use the interactive documentation at `http://localhost:8001/docs`.

Example task creation:
```json
{
  "title": "Prepare presentation for team meeting",
  "description": "Create slides covering quarterly results and upcoming initiatives",
  "user_id": "user123"
}
```

The AI will automatically classify the task with priority, category, estimated time, and potential subtasks.

## Supported AI Providers

The system supports multiple AI providers that are compatible with the OpenAI API format:
- OpenRouter (default)
- OpenAI
- Anthropic (via OpenRouter)
- Google models (via OpenRouter)
- Zhipu AI (via OpenRouter)
- Any other OpenAI-compatible API provider

## Model Management

The system supports dynamic model switching without restarting services:
1. Access the web interface at `http://localhost:5000`
2. Use the "AI Configuration" section to update settings
3. Enter your provider URL, API token, and model name
4. Click "Update Configuration" to apply changes immediately
5. Supported models include:
   - `qwen/qwen3-coder:free` (default)
   - `anthropic/claude-3-haiku:free`
   - `openai/gpt-4`
   - `z-ai/glm-4.5-air:free`
   - Any other OpenRouter-compatible model