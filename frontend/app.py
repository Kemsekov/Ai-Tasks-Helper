from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
import os

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
            data = request.json

            # Get current configuration to use for AI processing
            config_response = requests.get(f'{BACKEND_URL}/api/config')
            config = config_response.json()

            # Add the configuration parameters to the request
            params = {
                'provider_url': config.get('provider_url', 'https://openrouter.ai/api/v1'),
                'api_token': os.getenv('OPENROUTER_TOKEN', ''),  # Use token from environment as fallback
                'model_name': config.get('model', 'qwen/qwen3-coder:free')
            }

            # Make the request to the backend with parameters
            response = requests.post(f'{BACKEND_URL}/api/v1/tasks/', json=data, params=params)
            return jsonify(response.json()), response.status_code
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:  # GET request
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
            response = requests.delete(f'{BACKEND_URL}/api/v1/tasks/{task_id}')
            return jsonify(response.json()), response.status_code
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    elif request.method == 'GET':
        try:
            response = requests.get(f'{BACKEND_URL}/api/v1/tasks/{task_id}')
            return jsonify(response.json()), response.status_code
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    elif request.method == 'PUT':
        try:
            data = request.json
            response = requests.put(f'{BACKEND_URL}/api/v1/tasks/{task_id}', json=data)
            return jsonify(response.json()), response.status_code
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/static/<path:path>')
def send_static(path):
    from flask import send_from_directory
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)