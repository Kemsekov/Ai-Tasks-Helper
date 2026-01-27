from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import tasks

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