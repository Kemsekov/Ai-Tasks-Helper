document.addEventListener('DOMContentLoaded', function() {
    const taskForm = document.getElementById('taskForm');
    const userIdInput = document.getElementById('userId');
    const taskTitleInput = document.getElementById('taskTitle');
    const taskDescriptionInput = document.getElementById('taskDescription');
    const filterUserIdInput = document.getElementById('filterUserId');
    const loadTasksBtn = document.getElementById('loadTasksBtn');
    const tasksContainer = document.getElementById('tasksContainer');
    const tokenStatusDiv = document.getElementById('tokenStatus');
    const newTokenInput = document.getElementById('newToken');
    const updateTokenBtn = document.getElementById('updateTokenBtn');
    const currentModelDiv = document.getElementById('currentModel');
    const newModelInput = document.getElementById('newModel');
    const updateModelBtn = document.getElementById('updateModelBtn');

    // Add task form submission
    taskForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const userId = userIdInput.value.trim();
        const title = taskTitleInput.value.trim();
        const description = taskDescriptionInput.value.trim();
        
        if (!userId || !title) {
            showError('Username and task title are required');
            return;
        }
        
        try {
            showLoading(true);
            const response = await fetch('/api/tasks/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    title: title,
                    description: description,
                    user_id: userId
                })
            });
            
            if (response.ok) {
                const task = await response.json();
                showSuccess(`Task "${task.title}" added successfully!`);
                taskForm.reset();
                // Reload tasks for this user
                await loadTasks(userId);
            } else {
                const error = await response.json();
                showError(`Failed to add task: ${error.detail || 'Unknown error'}`);
            }
        } catch (error) {
            showError(`Error adding task: ${error.message}`);
        } finally {
            showLoading(false);
        }
    });

    // Load tasks button click
    loadTasksBtn.addEventListener('click', async function() {
        const userId = filterUserIdInput.value.trim();
        if (!userId) {
            showError('Please enter a username to load tasks');
            return;
        }
        
        await loadTasks(userId);
    });

    // Load tasks for a specific user
    async function loadTasks(userId) {
        try {
            showLoading(true);
            tasksContainer.innerHTML = '<div class="loading">Loading tasks...</div>';
            
            const response = await fetch(`/api/users/${encodeURIComponent(userId)}/tasks`);
            
            if (response.ok) {
                const tasks = await response.json();
                displayTasks(tasks, userId);
            } else {
                const error = await response.json();
                showError(`Failed to load tasks: ${error.detail || 'Unknown error'}`);
                tasksContainer.innerHTML = '';
            }
        } catch (error) {
            showError(`Error loading tasks: ${error.message}`);
            tasksContainer.innerHTML = '';
        } finally {
            showLoading(false);
        }
    }

    // Display tasks in the container
    function displayTasks(tasks, userId) {
        if (tasks.length === 0) {
            tasksContainer.innerHTML = `<div class="no-tasks">No tasks found for user "${userId}". Add some tasks!</div>`;
            return;
        }
        
        tasksContainer.innerHTML = '';
        
        tasks.forEach(task => {
            const taskCard = document.createElement('div');
            taskCard.className = 'task-card';
            taskCard.innerHTML = `
                <div class="task-title">${escapeHtml(task.title)}</div>
                <div class="task-description">${escapeHtml(task.description || 'No description')}</div>
                <div class="task-meta">
                    <div class="meta-item priority-${task.priority.toLowerCase()}">
                        <span>Priority:</span>
                        <strong>${task.priority}</strong>
                    </div>
                    <div class="meta-item category-${task.category.toLowerCase()}">
                        <span>Category:</span>
                        <strong>${task.category}</strong>
                    </div>
                    <div class="meta-item">
                        <span>Time:</span>
                        <strong>${task.estimated_time_minutes || 'N/A'} min</strong>
                    </div>
                </div>
                <div class="meta-item">
                    <small>AI Processed: ${task.ai_processed ? 'Yes' : 'No (using defaults)'}</small>
                </div>
                <div class="meta-item">
                    <small>Added: ${new Date(task.created_at).toLocaleString()}</small>
                </div>
                <button class="delete-btn" data-task-id="${task.id}">Delete Task</button>
            `;
            
            tasksContainer.appendChild(taskCard);
        });
        
        // Add event listeners to delete buttons
        document.querySelectorAll('.delete-btn').forEach(button => {
            button.addEventListener('click', async function() {
                const taskId = parseInt(this.getAttribute('data-task-id'));
                await deleteTask(taskId, userId);
            });
        });
    }

    // Delete a task
    async function deleteTask(taskId, userId) {
        if (!confirm('Are you sure you want to delete this task?')) {
            return;
        }
        
        try {
            showLoading(true);
            const response = await fetch(`/api/tasks/${taskId}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                showSuccess('Task deleted successfully!');
                // Reload tasks for this user
                await loadTasks(userId);
            } else {
                const error = await response.json();
                showError(`Failed to delete task: ${error.detail || 'Unknown error'}`);
            }
        } catch (error) {
            showError(`Error deleting task: ${error.message}`);
        } finally {
            showLoading(false);
        }
    }

    // Utility functions
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function showLoading(show) {
        const loadingIndicator = document.querySelector('.loading');
        if (show && !loadingIndicator) {
            tasksContainer.innerHTML = '<div class="loading">Loading...</div>';
        } else if (!show && loadingIndicator) {
            loadingIndicator.remove();
        }
    }

    function showError(message) {
        // Remove any existing alerts
        removeAlerts();
        
        const alertDiv = document.createElement('div');
        alertDiv.className = 'error';
        alertDiv.textContent = message;
        document.querySelector('.container').insertBefore(alertDiv, document.querySelector('section'));
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    function showSuccess(message) {
        // Remove any existing alerts
        removeAlerts();
        
        const alertDiv = document.createElement('div');
        alertDiv.className = 'success';
        alertDiv.textContent = message;
        document.querySelector('.container').insertBefore(alertDiv, document.querySelector('section'));
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 3000);
    }

    function removeAlerts() {
        document.querySelectorAll('.error, .success').forEach(el => el.remove());
    }

    // Check token status on page load
    async function checkTokenStatus() {
        try {
            const response = await fetch('/api/health');
            const status = await response.json();

            if (status.api_access) {
                tokenStatusDiv.innerHTML = `
                    <div class="token-status-container token-status-valid">
                        <strong>Status:</strong> Valid<br>
                        <strong>Message:</strong> ${status.message}
                    </div>
                `;
            } else {
                tokenStatusDiv.innerHTML = `
                    <div class="token-status-container token-status-invalid">
                        <strong>Status:</strong> Invalid<br>
                        <strong>Error:</strong> ${status.message}
                    </div>
                `;
            }
        } catch (error) {
            tokenStatusDiv.innerHTML = `
                <div class="token-status-container token-status-invalid">
                    <strong>Status:</strong> Error checking token<br>
                    <strong>Error:</strong> Could not connect to API
                </div>
            `;
        }
    }

    // Update token button click handler
    updateTokenBtn.addEventListener('click', async function() {
        const newToken = newTokenInput.value.trim();
        if (!newToken) {
            showError('Please enter a valid API token');
            return;
        }

        try {
            showLoading(true);
            const response = await fetch('/api/update-token', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ token: newToken })
            });

            const result = await response.json();

            if (result.status === 'success') {
                showSuccess(result.message);
                // Refresh token status after successful update
                setTimeout(checkTokenStatus, 1000);
                newTokenInput.value = ''; // Clear the input
            } else {
                showError(result.message);
            }
        } catch (error) {
            showError(`Error updating token: ${error.message}`);
        } finally {
            showLoading(false);
        }
    });

    // Check model status on page load
    async function checkCurrentModel() {
        try {
            const response = await fetch('/api/model');
            const result = await response.json();

            if (result.status === 'success') {
                currentModelDiv.innerHTML = `
                    <div class="token-status-container token-status-valid">
                        <strong>Current Model:</strong> ${result.model}
                    </div>
                `;
            } else {
                currentModelDiv.innerHTML = `
                    <div class="token-status-container token-status-invalid">
                        <strong>Error:</strong> Could not retrieve model
                    </div>
                `;
            }
        } catch (error) {
            currentModelDiv.innerHTML = `
                <div class="token-status-container token-status-invalid">
                    <strong>Error:</strong> Could not connect to API
                </div>
            `;
        }
    }

    // Update model button click handler
    updateModelBtn.addEventListener('click', async function() {
        const newModel = newModelInput.value.trim();
        if (!newModel) {
            showError('Please enter a valid model name');
            return;
        }

        try {
            showLoading(true);
            const response = await fetch('/api/update-model', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ token: newModel })  // Using token field to match backend expectation
            });

            const result = await response.json();

            if (result.status === 'success') {
                showSuccess(result.message);
                // Refresh model status after successful update
                setTimeout(checkCurrentModel, 1000);
                newModelInput.value = ''; // Clear the input
            } else {
                showError(result.message);
            }
        } catch (error) {
            showError(`Error updating model: ${error.message}`);
        } finally {
            showLoading(false);
        }
    });

    // Initialize token status check
    checkTokenStatus();

    // Initialize model status check
    checkCurrentModel();
});