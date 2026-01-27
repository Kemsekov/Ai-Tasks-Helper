import asyncio
import aiohttp
import json

# Base URL for the API
BASE_URL = "http://localhost:8001/api/v1"

async def add_task(session, title, description, user_id):
    """Add a new task via API"""
    url = f"{BASE_URL}/tasks/"
    payload = {
        "title": title,
        "description": description,
        "user_id": user_id
    }
    
    print(f"Adding task: {title}")
    async with session.post(url, json=payload) as response:
        result = await response.json()
        print(f"Response status: {response.status}")
        if response.status == 200:
            print(f"Task added successfully with ID: {result['id']}")
        else:
            print(f"Error adding task: {result}")
        print("-" * 50)
        return result if response.status == 200 else None

async def get_task(session, task_id):
    """Get a specific task by ID"""
    url = f"{BASE_URL}/tasks/{task_id}"
    
    print(f"Getting task with ID: {task_id}")
    async with session.get(url) as response:
        result = await response.json()
        print(f"Response status: {response.status}")
        if response.status == 200:
            print("Task details:")
            print(json.dumps(result, indent=2))
        else:
            print(f"Error getting task: {result}")
        print("-" * 50)
        return result if response.status == 200 else None

async def get_user_tasks(session, user_id):
    """Get all tasks for a specific user"""
    url = f"{BASE_URL}/users/{user_id}/tasks"
    
    print(f"Getting all tasks for user: {user_id}")
    async with session.get(url) as response:
        result = await response.json()
        print(f"Response status: {response.status}")
        if response.status == 200:
            print(f"Found {len(result)} tasks for user {user_id}")
            for i, task in enumerate(result, 1):
                print(f"  Task {i}: {task['title']} (Priority: {task['priority']})")
        else:
            print(f"Error getting user tasks: {result}")
        print("-" * 50)
        return result if response.status == 200 else None

async def delete_task(session, task_id):
    """Delete a task by ID"""
    url = f"{BASE_URL}/tasks/{task_id}"
    
    print(f"Deleting task with ID: {task_id}")
    async with session.delete(url) as response:
        result = await response.json()
        print(f"Response status: {response.status}")
        if response.status == 200:
            print(f"Task {task_id} deleted successfully")
        else:
            print(f"Error deleting task: {result}")
        print("-" * 50)
        return result if response.status == 200 else None

async def main():
    # Create an HTTP session
    async with aiohttp.ClientSession() as session:
        # Add several tasks for different users
        print("=== ADDING TASKS ===")
        
        # Add tasks for user1
        task1 = await add_task(session, "Complete project documentation", 
                              "Write comprehensive documentation for the AI task manager project", "user1")
        task2 = await add_task(session, "Fix login bug", 
                              "Resolve the authentication issue reported by QA team", "user1")
        
        # Add tasks for user2
        task3 = await add_task(session, "Buy groceries", 
                              "Milk, eggs, bread, fruits and vegetables", "user2")
        task4 = await add_task(session, "Schedule dentist appointment", 
                              "Call Dr. Smith's office to schedule a checkup", "user2")
        
        # Add one more task for user1
        task5 = await add_task(session, "Prepare presentation slides", 
                              "Create slides for the quarterly review meeting", "user1")
        
        print("\n=== RETRIEVING INDIVIDUAL TASKS ===")
        
        # Get individual tasks if they were created successfully
        if task1:
            await get_task(session, task1['id'])
        if task3:
            await get_task(session, task3['id'])
        
        print("\n=== RETRIEVING ALL TASKS FOR USER1 ===")
        # Get all tasks for user1
        user1_tasks = await get_user_tasks(session, "user1")
        
        print("\n=== RETRIEVING ALL TASKS FOR USER2 ===")
        # Get all tasks for user2
        user2_tasks = await get_user_tasks(session, "user2")
        
        print("\n=== UPDATING A TASK ===")
        # Update a task
        if task2:
            update_url = f"{BASE_URL}/tasks/{task2['id']}"
            update_payload = {
                "title": "Fix critical login bug",
                "priority": "High"
            }
            print(f"Updating task {task2['id']}")
            async with session.put(update_url, json=update_payload) as response:
                update_result = await response.json()
                print(f"Update response status: {response.status}")
                if response.status == 200:
                    print("Task updated successfully")
                    print(json.dumps(update_result, indent=2))
                else:
                    print(f"Error updating task: {update_result}")
        
        print("\n=== FINAL TASK LISTS ===")
        # Show final task lists
        await get_user_tasks(session, "user1")
        await get_user_tasks(session, "user2")

if __name__ == "__main__":
    asyncio.run(main())