import asyncio
import json
from httpx import AsyncClient
from main import app

async def test_create_task():
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        payload = {
            "title": "Complete project documentation",
            "description": "Write comprehensive documentation for the AI task manager project",
            "user_id": "test_user_123"
        }
        
        response = await ac.post("/api/v1/tasks/", json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            task_data = response.json()
            print(f"Created task ID: {task_data['id']}")
            print(f"Title: {task_data['title']}")
            print(f"Priority: {task_data['priority']}")
            print(f"Category: {task_data['category']}")
            print(f"Estimated Time: {task_data['estimated_time_minutes']} minutes")
            print(f"Subtasks: {task_data['subtasks']}")
            
            # Test getting the task
            task_id = task_data['id']
            get_response = await ac.get(f"/api/v1/tasks/{task_id}")
            print(f"\nRetrieved task: {get_response.json()}")
            
            # Test getting user's tasks
            user_tasks_response = await ac.get(f"/api/v1/users/test_user_123/tasks")
            print(f"\nUser tasks: {len(user_tasks_response.json())} tasks found")
            
            # Test deleting the task
            delete_response = await ac.delete(f"/api/v1/tasks/{task_id}")
            print(f"\nDelete response: {delete_response.json()}")

if __name__ == "__main__":
    asyncio.run(test_create_task())