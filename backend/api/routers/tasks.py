from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from models.database import get_session_local
from models.task import Task, PriorityEnum, CategoryEnum
from schemas.task import TaskCreate, TaskUpdate, TaskResponse
from utils.ai_classifier import classify_task_with_ai
from sqlalchemy.exc import IntegrityError
import os
import importlib

router = APIRouter()

@router.get("/api/health")
async def api_health(
    provider_url: str = Query(..., description="AI provider URL"),
    api_token: str = Query(..., description="API token for the provider"),
    model_name: str = Query("qwen/qwen3-coder:free", description="Model name to test")
):
    """Check if the AI provider API token is valid with specified model"""
    try:
        from openai import OpenAI
        # Create a temporary client with the provided parameters
        temp_client = OpenAI(
            base_url=provider_url,
            api_key=api_token
        )

        # Test the API with a simple request using the specified model
        response = temp_client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": "Hello, are you there?"}],
            max_tokens=5
        )
        return {
            "status": "healthy",
            "api_access": True,
            "message": f"AI provider API is accessible and token is valid with model {model_name}",
            "model": model_name
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "api_access": False,
            "message": f"AI provider API error: {str(e)}",
            "model": model_name
        }

def get_db():
    db = get_session_local()()
    try:
        yield db
    finally:
        db.close()

@router.post("/api/update-token")
async def update_token(token: str):
    """Update the OpenRouter API token"""
    try:
        # Update the client with the new token
        from openai import OpenAI
        global client
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=token
        )

        # Test the new token
        response = client.chat.completions.create(
            model="qwen/qwen3-coder:free",
            messages=[{"role": "user", "content": "Hello, are you there?"}],
            max_tokens=5
        )

        # Update environment variable (this won't persist after container restart)
        os.environ['OPENROUTER_TOKEN'] = token

        return {
            "status": "success",
            "message": "Token updated successfully and validated"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to validate new token: {str(e)}"
        }

@router.post("/tasks/")
async def create_task(
    task: TaskCreate,
    provider_url: str = Query(..., description="AI provider URL"),
    api_token: str = Query(..., description="API token for the provider"),
    model_name: str = Query("qwen/qwen3-coder:free", description="Model name to use for classification"),
    db: Session = Depends(get_db)
):
    # Use AI to classify the task with the provided parameters
    classification_result = await classify_task_with_ai(
        task.title,
        task.description or "",
        provider_url,
        api_token,
        model_name
    )

    # Create a new task with AI-classified data
    db_task = Task(
        title=task.title,
        description=task.description,
        priority=PriorityEnum(classification_result["priority"]),
        category=CategoryEnum(classification_result["category"]),
        estimated_time_minutes=classification_result["estimated_time_minutes"],
        subtasks=str(classification_result["subtasks"]) if classification_result["subtasks"] else None,
        user_id=task.user_id
    )

    try:
        db.add(db_task)
        db.commit()
        db.refresh(db_task)

        # Create a custom response that includes AI status information
        response_data = {
            "id": db_task.id,
            "title": db_task.title,
            "description": db_task.description,
            "priority": db_task.priority.value,
            "category": db_task.category.value,
            "estimated_time_minutes": db_task.estimated_time_minutes,
            "subtasks": db_task.subtasks,
            "user_id": db_task.user_id,
            "created_at": db_task.created_at,
            "updated_at": db_task.updated_at,
            "ai_processed": not classification_result.get("used_fallback", False)
        }
        return response_data
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error creating task")

@router.get("/tasks/{task_id}")
def read_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # For existing tasks, we don't know if AI was used, so we'll default to false
    response_data = {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "priority": task.priority.value,
        "category": task.category.value,
        "estimated_time_minutes": task.estimated_time_minutes,
        "subtasks": task.subtasks,
        "user_id": task.user_id,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
        "ai_processed": False  # For existing tasks, we don't know the AI status
    }
    return response_data

@router.get("/users/{user_id}/tasks")
def read_user_tasks(user_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tasks = db.query(Task).filter(Task.user_id == user_id).offset(skip).limit(limit).all()

    # Convert tasks to response format with ai_processed field
    response_tasks = []
    for task in tasks:
        response_data = {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority.value,
            "category": task.category.value,
            "estimated_time_minutes": task.estimated_time_minutes,
            "subtasks": task.subtasks,
            "user_id": task.user_id,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
            "ai_processed": False  # For existing tasks, we don't know the AI status
        }
        response_tasks.append(response_data)

    return response_tasks

@router.put("/tasks/{task_id}")
def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update task fields if provided
    update_data = task_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)

    db.commit()
    db.refresh(db_task)

    # Return updated task with ai_processed field
    response_data = {
        "id": db_task.id,
        "title": db_task.title,
        "description": db_task.description,
        "priority": db_task.priority.value,
        "category": db_task.category.value,
        "estimated_time_minutes": db_task.estimated_time_minutes,
        "subtasks": db_task.subtasks,
        "user_id": db_task.user_id,
        "created_at": db_task.created_at,
        "updated_at": db_task.updated_at,
        "ai_processed": False  # For updated tasks, we don't know the AI status
    }
    return response_data

@router.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully"}