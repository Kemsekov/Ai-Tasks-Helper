import yaml
from typing import Dict, Optional
from openai import OpenAI
from config import settings

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.openrouter_token  # Get from https://openrouter.ai
)

async def classify_task_with_ai(task_title: str, task_description: str) -> Optional[Dict]:
    """
    Classify a task using AI and return structured data in YAML format
    """
    prompt = f"""
    Analyze the following task and provide classification in YAML format:
    
    Task Title: {task_title}
    Task Description: {task_description}
    
    Please provide the following information in YAML format:
    - priority: High, Medium, or Low
    - category: Work, Personal, Learning, Health, or Other
    - estimated_time_minutes: Approximate time in minutes to complete the task
    - subtasks: A list of subtasks if applicable, otherwise null
    
    Example format:
    ```yaml
    priority: High
    category: Work
    estimated_time_minutes: 60
    subtasks:
      - Research requirements
      - Draft initial proposal
    ```
    
    Only respond with the YAML content, nothing else.
    """
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="qwen/qwen3-coder:free",  # Free Qwen3 Coder model
                messages=[
                    {"role": "system", "content": "You are an expert task classifier. Respond only with valid YAML format as requested."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            # Extract the response content
            content = response.choices[0].message.content.strip()
            
            # Remove markdown code block markers if present
            if content.startswith("```yaml") and content.endswith("```"):
                content = content[7:-3].strip()
            elif content.startswith("```") and content.endswith("```"):
                content = content[3:-3].strip()
            
            # Parse the YAML response
            parsed_response = yaml.safe_load(content)
            
            # Validate the response structure
            if validate_classification(parsed_response):
                return {
                    "priority": parsed_response["priority"],
                    "category": parsed_response["category"],
                    "estimated_time_minutes": parsed_response.get("estimated_time_minutes"),
                    "subtasks": parsed_response.get("subtasks")
                }
            else:
                continue  # Retry if validation fails
                
        except Exception as e:
            print(f"Error in AI classification (attempt {attempt + 1}): {str(e)}")
            if attempt == max_retries - 1:
                # Return default values if all retries fail
                return {
                    "priority": "Medium",
                    "category": "Other",
                    "estimated_time_minutes": 30,
                    "subtasks": None
                }
    
    # If all attempts fail, return default values
    return {
        "priority": "Medium",
        "category": "Other",
        "estimated_time_minutes": 30,
        "subtasks": None
    }

def validate_classification(data: Dict) -> bool:
    """
    Validate the classification data returned by AI
    """
    if not isinstance(data, dict):
        return False
    
    # Check required fields
    required_fields = ["priority", "category"]
    for field in required_fields:
        if field not in data:
            return False
    
    # Validate priority
    if data["priority"] not in ["High", "Medium", "Low"]:
        return False
    
    # Validate category
    if data["category"] not in ["Work", "Personal", "Learning", "Health", "Other"]:
        return False
    
    # Validate estimated_time_minutes if present
    if "estimated_time_minutes" in data and data["estimated_time_minutes"] is not None:
        if not isinstance(data["estimated_time_minutes"], int) or data["estimated_time_minutes"] <= 0:
            return False
    
    # Validate subtasks if present
    if "subtasks" in data and data["subtasks"] is not None:
        if not isinstance(data["subtasks"], list):
            return False
        for subtask in data["subtasks"]:
            if not isinstance(subtask, str):
                return False
    
    return True