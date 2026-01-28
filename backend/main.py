from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from api.routers import tasks
from openai import OpenAI
import os

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

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Global client and model for API health checks
current_model = os.getenv("DEFAULT_MODEL", "qwen/qwen3-coder:free")
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_TOKEN")  # Get from https://openrouter.ai
)

@app.get("/api/health")
async def api_health():
    """Check if the OpenRouter API token is valid with the current model"""
    try:
        # Test the API with a simple request using the current model
        response = client.chat.completions.create(
            model=current_model,  # Use the current model instead of hardcoded one
            messages=[{"role": "user", "content": "Hello, are you there?"}],
            max_tokens=5
        )
        return {
            "status": "healthy",
            "api_access": True,
            "message": f"OpenRouter API is accessible and token is valid with model {current_model}",
            "model": current_model
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "api_access": False,
            "message": f"OpenRouter API error: {str(e)}",
            "model": current_model
        }

from fastapi import FastAPI, Query
from pydantic import BaseModel

class TokenUpdateRequest(BaseModel):
    token: str

@app.post("/api/update-token")
async def update_token(request: TokenUpdateRequest):
    """Update the OpenRouter API token"""
    try:
        # Update the client with the new token
        global client
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=request.token
        )

        # Test the new token
        response = client.chat.completions.create(
            model="qwen/qwen3-coder:free",
            messages=[{"role": "user", "content": "Hello, are you there?"}],
            max_tokens=5
        )

        # Update environment variable (this won't persist after container restart)
        os.environ['OPENROUTER_TOKEN'] = request.token

        return {
            "status": "success",
            "message": "Token updated successfully and validated"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to validate new token: {str(e)}"
        }

@app.get("/api/model")
async def get_current_model():
    """Get the current model being used"""
    return {
        "model": current_model,
        "status": "success"
    }

@app.post("/api/update-model")
async def update_model(request: TokenUpdateRequest):
    """Update the model being used"""
    global current_model
    current_model = request.token  # Store the new model name

    # Update environment variable (this won't persist after container restart)
    os.environ['DEFAULT_MODEL'] = request.token

    return {
        "status": "success",
        "message": f"Model updated to {request.token}",
        "model": request.token
    }