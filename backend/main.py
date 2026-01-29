import os
import logging
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from api.routers import tasks
from pydantic import BaseModel

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Task Manager", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, configure this properly
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tasks.router, prefix="/api/v1", tags=["tasks"])

@app.get("/")
def read_root():
    return {"message": "AI Task Manager API"}

# Define the request models first
class TokenUpdateRequest(BaseModel):
    token: str

class ConfigUpdateRequest(BaseModel):
    provider_url: str
    api_token: str
    model_name: str

# Global variables for current provider settings
current_provider_url = "https://openrouter.ai/api/v1"  # Default provider URL
current_api_token = os.getenv("OPENROUTER_TOKEN", "")  # Default to environment variable
current_model = os.getenv("DEFAULT_MODEL", "qwen/qwen3-coder:free")

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/api/config")
def get_current_config():
    return {
        "provider_url": current_provider_url,
        "model": current_model,
        "api_token": current_api_token,  # Include the token in the response
        "has_valid_token": bool(current_api_token),
        "status": "success"
    }

@app.get("/api/health")
def api_health_check(
    provider_url: str = Query(None, description="Provider URL to test"),
    api_token: str = Query(None, description="API token to test"),
    model_name: str = Query(None, description="Model name to test")
):
    """Check if the AI provider API token is valid with specified model"""
    # Use provided parameters or fall back to current configuration
    test_url = provider_url or current_provider_url
    test_token = api_token or current_api_token
    test_model = model_name or current_model

    try:
        from openai import OpenAI
        import httpx

        # Create headers for OpenRouter
        headers = {
            "Authorization": f"Bearer {test_token}",
            "Content-Type": "application/json"
        }

        # Add referer header for OpenRouter free tier access
        if "openrouter.ai" in test_url:
            headers["HTTP-Referer"] = "http://localhost:8000"  # Local development
            headers["X-Title"] = "AI Task Helper"  # App name for OpenRouter analytics

        # Create a temporary client with the provided parameters
        http_client = httpx.Client(headers=headers)
        temp_client = OpenAI(
            base_url=test_url,
            api_key=test_token,
            http_client=http_client
        )

        # Test the API with a simple request using the specified model
        response = temp_client.chat.completions.create(
            model=test_model,
            messages=[{"role": "user", "content": "Hello, are you there?"}],
            max_tokens=5
        )
        return {
            "status": "healthy",
            "api_access": True,
            "message": f"AI provider API is accessible and token is valid with model {test_model}",
            "model": test_model
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "api_access": False,
            "message": f"AI provider API error: {str(e)}",
            "model": test_model
        }

@app.post("/api/update-config")
def update_current_config(request: ConfigUpdateRequest):
    global current_provider_url, current_api_token, current_model
    current_provider_url = request.provider_url
    current_api_token = request.api_token
    current_model = request.model_name
    return {
        "status": "success",
        "message": f"Configuration updated - Provider: {request.provider_url}, Model: {request.model_name}",
        "config": {
            "provider_url": request.provider_url,
            "model": request.model_name,
            "has_valid_token": True
        }
    }

