import asyncio
import json
import sys
import os
from unittest.mock import patch

# Add backend to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from httpx import AsyncClient
from main import app

async def mock_classify_task_with_ai(task_title: str, task_description: str):
    """Mock AI classification function for testing"""
    return {
        "priority": "Medium",
        "category": "Work",
        "estimated_time_minutes": 30,
        "subtasks": ["Step 1", "Step 2"]
    }

async def test_api_calls():
    # Patch the AI function to avoid actual API calls
    with patch('api.routers.tasks.classify_task_with_ai', side_effect=mock_classify_task_with_ai):
        async with AsyncClient(app=app, base_url="http://testserver") as ac:
            print("=== ADDING TASKS ===")

            # Add a few tasks
            tasks_to_add = [
                {
                    "title": "Complete project documentation",
                    "description": "Write comprehensive documentation for the AI task manager project",
                    "user_id": "user1"
                },
                {
                    "title": "Fix login bug",
                    "description": "Resolve the authentication issue reported by QA team",
                    "user_id": "user1"
                },
                {
                    "title": "Buy groceries",
                    "description": "Milk, eggs, bread, fruits and vegetables",
                    "user_id": "user2"
                },
                {
                    "title": "Schedule dentist appointment",
                    "description": "Call Dr. Smith's office to schedule a checkup",
                    "user_id": "user2"
                }
            ]

            created_tasks = []
            for i, task_data in enumerate(tasks_to_add, 1):
                print(f"\nAdding task {i}: {task_data['title']}")
                response = await ac.post("/api/v1/tasks/", json=task_data)

                if response.status_code == 200:
                    task = response.json()
                    print(f"✓ Task created successfully with ID: {task['id']}")
                    print(f"  Title: {task['title']}")
                    print(f"  Priority: {task['priority']}")
                    print(f"  Category: {task['category']}")
                    print(f"  Estimated time: {task['estimated_time_minutes']} minutes")
                    print(f"  Subtasks: {task['subtasks']}")
                    created_tasks.append(task)
                else:
                    print(f"✗ Failed to create task: {response.status_code} - {response.text}")

            print(f"\n=== RETRIEVING INDIVIDUAL TASKS ===")
            # Get specific tasks
            for task in created_tasks[:2]:  # Just get first 2 tasks
                print(f"\nGetting task ID: {task['id']}")
                response = await ac.get(f"/api/v1/tasks/{task['id']}")

                if response.status_code == 200:
                    retrieved_task = response.json()
                    print(f"✓ Retrieved task: {retrieved_task['title']}")
                    print(json.dumps(retrieved_task, indent=2))
                else:
                    print(f"✗ Failed to retrieve task: {response.status_code} - {response.text}")

            print(f"\n=== RETRIEVING ALL TASKS FOR USER1 ===")
            # Get all tasks for user1
            response = await ac.get("/api/v1/users/user1/tasks")
            if response.status_code == 200:
                user1_tasks = response.json()
                print(f"✓ Found {len(user1_tasks)} tasks for user1:")
                for i, task in enumerate(user1_tasks, 1):
                    print(f"  {i}. {task['title']} (Priority: {task['priority']})")
            else:
                print(f"✗ Failed to retrieve user1 tasks: {response.status_code} - {response.text}")

            print(f"\n=== RETRIEVING ALL TASKS FOR USER2 ===")
            # Get all tasks for user2
            response = await ac.get("/api/v1/users/user2/tasks")
            if response.status_code == 200:
                user2_tasks = response.json()
                print(f"✓ Found {len(user2_tasks)} tasks for user2:")
                for i, task in enumerate(user2_tasks, 1):
                    print(f"  {i}. {task['title']} (Priority: {task['priority']})")
            else:
                print(f"✗ Failed to retrieve user2 tasks: {response.status_code} - {response.text}")

            print(f"\n=== UPDATING A TASK ===")
            # Update a task if we have any
            if created_tasks:
                task_to_update = created_tasks[0]
                print(f"Updating task ID: {task_to_update['id']}")

                update_data = {
                    "title": f"Updated: {task_to_update['title']}",
                    "priority": "High"
                }

                response = await ac.put(f"/api/v1/tasks/{task_to_update['id']}", json=update_data)
                if response.status_code == 200:
                    updated_task = response.json()
                    print(f"✓ Task updated successfully")
                    print(f"  New title: {updated_task['title']}")
                    print(f"  New priority: {updated_task['priority']}")
                else:
                    print(f"✗ Failed to update task: {response.status_code} - {response.text}")

            print(f"\n=== FINAL TASK LISTS ===")
            # Show final state
            response = await ac.get("/api/v1/users/user1/tasks")
            if response.status_code == 200:
                user1_tasks = response.json()
                print(f"Final count for user1: {len(user1_tasks)} tasks")

            response = await ac.get("/api/v1/users/user2/tasks")
            if response.status_code == 200:
                user2_tasks = response.json()
                print(f"Final count for user2: {len(user2_tasks)} tasks")

            print(f"\n=== DELETING TASKS ===")
            # Clean up by deleting the tasks
            for task in created_tasks:
                print(f"Deleting task ID: {task['id']}")
                response = await ac.delete(f"/api/v1/tasks/{task['id']}")
                if response.status_code == 200:
                    print(f"✓ Task {task['id']} deleted successfully")
                else:
                    print(f"✗ Failed to delete task: {response.status_code} - {response.text}")

if __name__ == "__main__":
    asyncio.run(test_api_calls())