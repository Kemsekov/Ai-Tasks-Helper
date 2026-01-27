from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from models.database import get_session_local
from models.task import Task, PriorityEnum, CategoryEnum
from schemas.task import TaskCreate, TaskUpdate, TaskResponse
from utils.ai_classifier import classify_task_with_ai
from sqlalchemy.exc import IntegrityError

router = APIRouter()

def get_db():
    db = get_session_local()()
    try:
        yield db
    finally:
        db.close()

@router.post("/tasks/", response_model=TaskResponse)
async def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    # Use AI to classify the task
    classification_result = await classify_task_with_ai(task.title, task.description or "")
    
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
        return db_task
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error creating task")

@router.get("/tasks/{task_id}", response_model=TaskResponse)
def read_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.get("/users/{user_id}/tasks", response_model=List[TaskResponse])
def read_user_tasks(user_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tasks = db.query(Task).filter(Task.user_id == user_id).offset(skip).limit(limit).all()
    return tasks

@router.put("/tasks/{task_id}", response_model=TaskResponse)
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
    return db_task

@router.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully"}