import logging
import yaml
from typing import Dict, Optional
from openai import OpenAI
import httpx

# Set up logging
logger = logging.getLogger(__name__)

async def classify_task_with_ai(task_title: str, task_description: str, provider_url: str, api_token: str, model_name: str) -> Optional[Dict]:
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
      - Review with stakeholders
    ```

    Only respond with the YAML content, nothing else.
    """

    # Log the parameters for debugging
    logger.info(f"Attempting AI classification with provider: {provider_url}")
    logger.info(f"Model: {model_name}")
    logger.info(f"Token provided: {'Yes' if api_token else 'No'}")
    logger.info(f"Token length: {len(api_token) if api_token else 0}")

    # Create a client with the provided parameters and custom headers for OpenRouter
    # OpenRouter sometimes requires additional headers for authentication
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }

    # Add referer header for OpenRouter free tier access
    if "openrouter.ai" in provider_url:
        headers["HTTP-Referer"] = "http://localhost:8000"  # Local development
        headers["X-Title"] = "AI Task Helper"  # App name for OpenRouter analytics

    # Create custom httpx client with headers
    http_client = httpx.Client(headers=headers)

    client = OpenAI(
        base_url=provider_url,
        api_key=api_token,
        http_client=http_client
    )

    max_retries = 3
    for attempt in range(max_retries):
        try:
            logger.info(f"Making API call to {provider_url}/chat/completions, attempt {attempt + 1}")
            logger.info(f"Using model: {model_name}")

            response = client.chat.completions.create(
                model=model_name,  # Use the provided model
                messages=[
                    {"role": "system", "content": "You are an expert task classifier. Respond only with valid YAML format as requested."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )

            logger.info(f"API call successful, response type: {type(response)}")

            # Check if response is valid before accessing attributes
            if not hasattr(response, 'choices') or not response.choices:
                logger.error(f"Invalid response structure on attempt {attempt + 1}: {type(response)}")
                continue

            # Extract the response content
            content = response.choices[0].message.content.strip()
            logger.info(f"Response content preview: {content[:100]}...")

            # Remove markdown code block markers if present
            if content.startswith("```yaml") and content.endswith("```"):
                content = content[7:-3].strip()
            elif content.startswith("```") and content.endswith("```"):
                content = content[3:-3].strip()

            # Parse the YAML response
            parsed_response = yaml.safe_load(content)

            # Validate the response structure
            if validate_classification(parsed_response):
                logger.info("Classification successful, returning parsed response")
                return {
                    "priority": parsed_response["priority"],
                    "category": parsed_response["category"],
                    "estimated_time_minutes": parsed_response.get("estimated_time_minutes"),
                    "subtasks": parsed_response.get("subtasks"),
                    "used_fallback": False
                }
            else:
                logger.warning(f"Parsed response failed validation on attempt {attempt + 1}")
                continue  # Retry if validation fails

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error in AI classification (attempt {attempt + 1}): {error_msg}")
            logger.exception("Full traceback:")  # This will log the full stack trace

            # Check if it's an authentication error
            if "401" in error_msg or "User not found" in error_msg or "Authentication" in error_msg:
                logger.error("Authentication error detected - returning default values immediately")
                break  # Don't retry if it's an auth error
            elif "429" in error_msg or "rate" in error_msg.lower():
                logger.warning("Rate limit error detected - continuing to retry")
                continue  # Continue retrying for rate limits
            elif "Connection error" in error_msg or "connection" in error_msg.lower():
                logger.error(f"Connection error on attempt {attempt + 1}, will retry: {error_msg}")
                if attempt == max_retries - 1:
                    logger.error("All connection retries exhausted - returning default values")
                    return {
                        "priority": "Medium",
                        "category": "Other",
                        "estimated_time_minutes": 30,
                        "subtasks": None
                    }
            elif attempt == max_retries - 1:
                # Return default values if all retries fail
                logger.error("All retries exhausted - returning default values")
                return {
                    "priority": "Medium",
                    "category": "Other",
                    "estimated_time_minutes": 30,
                    "subtasks": None
                }

    # If all attempts fail or auth error occurs, return default values
    logger.warning("Returning fallback values after all attempts")
    return {
        "priority": "Medium",
        "category": "Other",
        "estimated_time_minutes": 30,
        "subtasks": None,
        "used_fallback": True
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