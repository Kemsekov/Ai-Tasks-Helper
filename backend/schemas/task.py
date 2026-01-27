from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

class PriorityEnum(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class CategoryEnum(str, Enum):
    WORK = "Work"
    PERSONAL = "Personal"
    LEARNING = "Learning"
    HEALTH = "Health"
    OTHER = "Other"

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    user_id: str

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[PriorityEnum] = None
    category: Optional[CategoryEnum] = None
    estimated_time_minutes: Optional[int] = None
    subtasks: Optional[str] = None

class TaskResponse(TaskBase):
    id: int
    priority: PriorityEnum
    category: CategoryEnum
    estimated_time_minutes: Optional[int] = None
    subtasks: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True