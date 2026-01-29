import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Get backend URL from environment variable or default to localhost
BACKEND_URL = os.environ.get('BACKEND_URL', 'http://backend:8000')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/tasks/', methods=['GET', 'POST'])
def handle_tasks():
    if request.method == 'POST':
        try:
            logger.info(f"Received task creation request: {request.json}")

            data = request.json

            # Get current configuration to use for AI processing
            config_response = requests.get(f'{BACKEND_URL}/api/config')
            config = config_response.json()

            logger.info(f"Current backend configuration: provider={config.get('provider_url')}, model={config.get('model')}")

            # Use the configuration from the backend - these are the values stored in the backend
            params = {
                'provider_url': config.get('provider_url', 'https://openrouter.ai/api/v1'),
                'api_token': config.get('api_token', '') if 'api_token' in config else config.get('current_api_token', ''),
                'model_name': config.get('model', 'qwen/qwen3-coder:free')
            }

            # Make the request to the backend with parameters
            response = requests.post(f'{BACKEND_URL}/api/v1/tasks/', json=data, params=params)
            logger.info(f"Backend response status: {response.status_code}")

            result = response.json()
            logger.info(f"Task created successfully: ID={result.get('id')}, Title={result.get('title')}")

            return jsonify(result), response.status_code
        except Exception as e:
            logger.error(f"Error in task creation: {str(e)}")
            return jsonify({'error': str(e)}), 500
    else:  # GET request
        logger.warning("GET method not allowed on /api/tasks/ endpoint")
        return jsonify({'error': 'GET not allowed on this endpoint'}), 405

@app.route('/api/users/<user_id>/tasks', methods=['GET'])
def get_user_tasks(user_id):
    try:
        response = requests.get(f'{BACKEND_URL}/api/v1/users/{user_id}/tasks')
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def api_health():
    try:
        response = requests.get(f'{BACKEND_URL}/health')
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/update-token', methods=['POST'])
def update_token():
    try:
        data = request.json
        token = data.get('token')
        if not token:
            return jsonify({'status': 'error', 'message': 'Token is required'}), 400

        # Forward the request to the backend
        response = requests.post(f'{BACKEND_URL}/api/update-token', json={'token': token})
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/config', methods=['GET'])
def get_config():
    try:
        response = requests.get(f'{BACKEND_URL}/api/config')
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/update-config', methods=['POST'])
def update_config():
    try:
        data = request.json
        # Validate required fields
        required_fields = ['provider_url', 'api_token', 'model_name']
        for field in required_fields:
            if field not in data:
                return jsonify({'status': 'error', 'message': f'{field} is required'}), 400

        # Forward the request to the backend
        response = requests.post(f'{BACKEND_URL}/api/update-config', json={
            'provider_url': data['provider_url'],
            'api_token': data['api_token'],
            'model_name': data['model_name']
        })
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks/<int:task_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_task(task_id):
    if request.method == 'DELETE':
        try:
            logger.info(f"Received request to delete task ID: {task_id}")
            response = requests.delete(f'{BACKEND_URL}/api/v1/tasks/{task_id}')
            logger.info(f"Task ID {task_id} deleted successfully")
            return jsonify(response.json()), response.status_code
        except Exception as e:
            logger.error(f"Error deleting task {task_id}: {str(e)}")
            return jsonify({'error': str(e)}), 500
    elif request.method == 'GET':
        try:
            logger.info(f"Received request to get task ID: {task_id}")
            response = requests.get(f'{BACKEND_URL}/api/v1/tasks/{task_id}')
            result = response.json()
            logger.info(f"Retrieved task ID {task_id}: {result.get('title', 'Unknown title')}")
            return jsonify(result), response.status_code
        except Exception as e:
            logger.error(f"Error getting task {task_id}: {str(e)}")
            return jsonify({'error': str(e)}), 500
    elif request.method == 'PUT':
        try:
            logger.info(f"Received request to update task ID: {task_id}, data: {request.json}")
            data = request.json
            # Forward the request to the backend
            response = requests.put(f'{BACKEND_URL}/api/v1/tasks/{task_id}', json=data)
            result = response.json()
            logger.info(f"Task ID {task_id} updated successfully")
            return jsonify(result), response.status_code
        except Exception as e:
            logger.error(f"Error updating task {task_id}: {str(e)}")
            return jsonify({'error': str(e)}), 500

@app.route('/static/<path:path>')
def send_static(path):
    from flask import send_from_directory
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)