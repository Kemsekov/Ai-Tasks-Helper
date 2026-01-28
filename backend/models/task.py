from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from enum import Enum

from .database import Base

class PriorityEnum(Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class CategoryEnum(Enum):
    WORK = "Work"
    PERSONAL = "Personal"
    LEARNING = "Learning"
    HEALTH = "Health"
    OTHER = "Other"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    priority = Column(SQLEnum(PriorityEnum), nullable=False)
    category = Column(SQLEnum(CategoryEnum), nullable=False)
    estimated_time_minutes = Column(Integer)  # Estimated time in minutes
    subtasks = Column(Text)  # JSON string of subtasks
    user_id = Column(String, nullable=False, index=True)  # Simple user identification
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)