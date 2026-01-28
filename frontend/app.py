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
            response = requests.post(f'{BACKEND_URL}/api/v1/tasks/', json=data)
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
        response = requests.get(f'{BACKEND_URL}/api/health')
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

@app.route('/api/model', methods=['GET'])
def get_model():
    try:
        response = requests.get(f'{BACKEND_URL}/api/model')
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/update-model', methods=['POST'])
def update_model():
    try:
        data = request.json
        model = data.get('token')  # Using 'token' field to be consistent with the backend request model
        if not model:
            return jsonify({'status': 'error', 'message': 'Model is required'}), 400

        # Forward the request to the backend
        response = requests.post(f'{BACKEND_URL}/api/update-model', json={'token': model})
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