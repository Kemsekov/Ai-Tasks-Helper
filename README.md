# AI Task Manager

An intelligent task management system that uses AI to automatically analyze and categorize tasks.

## Features

- **Add tasks in natural language**
- **AI-powered task classification** (priority, category, estimated time)
- **AI-generated subtasks** for complex tasks
- **Web-based AI configuration** (provider URL, API token, model name)
- **Persistent configuration storage** in browser cookies
- **Real-time AI token and model management**
- **Dynamic model switching** (supports Qwen, Claude, OpenAI, Google models, and other providers)
- **Configuration validation** to test provider connectivity
- **RESTful API** for task management
- **User-specific task organization**
- **PostgreSQL database storage**
- **Web-based frontend with intuitive UI**
- **Docker containerization** for easy deployment

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
2. Build and run with Docker Compose:

```bash
docker-compose up --build
```

**Note**: AI provider settings (provider URL, API token, and model name) must be configured through the web UI after launching the application. See the Web Interface section below for details.

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

# AI settings (these can be left as defaults - actual settings configured via web UI)
OPENROUTER_TOKEN= # Leave empty, configure via web UI
DEFAULT_MODEL="qwen/qwen3-coder:free" # This can be changed via web UI
```

## Services

The application consists of three main services:
- **PostgreSQL**: Database storage
- **Backend**: FastAPI server with AI integration
- **Frontend**: Flask server with web interface

## API Endpoints

### Backend API (available at http://localhost:8001/api/v1/)
- `POST /api/v1/tasks/` - Create a new task (requires provider_url, api_token, model_name query parameters, AI will classify it with priority, category, estimated time, and subtasks)
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
- **Configure AI Provider Settings**: Set your provider URL, API token, and model name through the dedicated configuration section
- **Validate Configuration**: Test your provider credentials and model availability with the validation feature
- **Persistent Configuration**: Settings are stored in browser cookies and persist across sessions
- **View and manage tasks** with a clean UI
- **Switch between different AI models** (Qwen, Claude, GPT, Gemini, etc.) without restarting
- **Monitor token and model status**
- **View AI-generated subtasks** for complex tasks
- **Add, view, update, and delete tasks**

**Important**: The AI provider settings (provider URL, API token, and model name) must be configured through the web UI. The application will not work properly until these are set via the configuration panel.

## Usage

After starting the service, access the web interface at `http://localhost:5000` to manage your tasks.

From the web interface, you can:
1. **Configure your AI provider settings** using the configuration panel (provider URL, token, model)
2. **Validate your configuration** to ensure connectivity
3. **Add tasks in natural language**
4. **View AI-generated subtasks** when applicable
5. **View, update, and delete your tasks**

Alternatively, you can interact with the API directly or use the interactive documentation at `http://localhost:8001/docs`.

Example task creation:
```json
{
  "title": "Plan birthday party",
  "description": "Organize a surprise birthday party including venue booking, catering, invitations, and entertainment",
  "user_id": "user123"
}
```

The AI will automatically classify the task with priority, category, estimated time, and generate subtasks if applicable.

## Supported AI Providers

The system supports multiple AI providers that are compatible with the OpenAI API format:
- OpenRouter (default)
- OpenAI
- Anthropic (via OpenRouter)
- Google models (via OpenRouter)
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
   - `google/gemma-2-9b:free`
   - `z-ai/glm-4.5-air:free`
   - Any other OpenRouter-compatible model

## Subtask Generation

The AI will automatically generate subtasks for complex tasks when appropriate. Subtasks appear in the task details when expanded in the web interface. The system intelligently determines when a task should be broken down into smaller, actionable items.