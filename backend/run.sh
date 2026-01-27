#!/bin/bash

# Load environment variables
set -a
source .env
set +a

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install PostgreSQL client tools for health checks
apt-get update && apt-get install -y postgresql-client

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
while ! pg_isready -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER
do
    sleep 1
done
echo "PostgreSQL is ready!"

# Run database migrations (create tables)
python -c "
import sys
import os
sys.path.append('.')

# Import settings first to initialize the database connection
from config.settings import settings

# Import models after settings to ensure proper initialization
from models.database import get_engine
from models.task import Task
from models.database import Base

# Create tables
engine = get_engine()
Base.metadata.create_all(bind=engine)
print('Database tables created successfully!')
"

# Run the FastAPI application with auto-reload enabled
exec uvicorn main:app --host $BACKEND_INTERNAL_HOST --port $BACKEND_INTERNAL_PORT --reload