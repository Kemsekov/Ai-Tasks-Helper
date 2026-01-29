document.addEventListener('DOMContentLoaded', function() {
    const taskForm = document.getElementById('taskForm');
    const userIdInput = document.getElementById('userId');
    const taskTitleInput = document.getElementById('taskTitle');
    const taskDescriptionInput = document.getElementById('taskDescription');
    const filterUserIdInput = document.getElementById('filterUserId');
    const loadTasksBtn = document.getElementById('loadTasksBtn');
    const tasksContainer = document.getElementById('tasksContainer');
    const configStatusDiv = document.getElementById('configStatus');
    const providerUrlInput = document.getElementById('providerUrl');
    const apiTokenInput = document.getElementById('apiToken');
    const modelNameInput = document.getElementById('modelName');
    const updateConfigBtn = document.getElementById('updateConfigBtn');
    const checkConfigBtn = document.getElementById('checkConfigBtn');

    // Define missing elements that are referenced later in the code
    const tokenStatusDiv = document.getElementById('tokenStatus');  // This element doesn't exist in current HTML
    const newTokenInput = document.getElementById('newToken');      // This element doesn't exist in current HTML
    const updateTokenBtn = document.getElementById('updateTokenBtn'); // This element doesn't exist in current HTML
    const currentModelDiv = document.getElementById('currentModel'); // This element doesn't exist in current HTML
    const newModelInput = document.getElementById('newModel');      // This element doesn't exist in current HTML
    const updateModelBtn = document.getElementById('updateModelBtn'); // This element doesn't exist in current HTML
    const checkTokenModelBtn = document.getElementById('checkTokenModelBtn'); // This element doesn't exist in current HTML

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
                ${task.subtasks ? `
                <div class="subtasks-section">
                    <details>
                        <summary><strong>Subtasks:</strong></summary>
                        <ul class="subtasks-list">
                            ${(JSON.parse(task.subtasks) || []).map(st => `<li>${st}</li>`).join('')}
                        </ul>
                    </details>
                </div>
                ` : ''}
                <div class="meta-item">
                    <small>Added: ${new Date(task.created_at).toLocaleString()}</small>
                </div>
                <button class="edit-btn" data-task-id="${task.id}">Edit Task</button>
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

        // Add event listeners to edit buttons
        document.querySelectorAll('.edit-btn').forEach(button => {
            button.addEventListener('click', function() {
                const taskId = parseInt(this.getAttribute('data-task-id'));
                openEditModal(taskId);
            });
        });
    }

    // Open edit modal for a task
    async function openEditModal(taskId) {
        try {
            showLoading(true);

            // Get the current task details from the API
            const response = await fetch(`/api/tasks/${taskId}`);
            const task = await response.json();

            if (!response.ok) {
                throw new Error(task.detail || 'Failed to fetch task details');
            }

            // Create and show edit modal
            const modal = document.createElement('div');
            modal.className = 'modal';
            modal.innerHTML = `
                <div class="modal-content">
                    <span class="close-modal">&times;</span>
                    <h3>Edit Task</h3>
                    <form id="editTaskForm">
                        <input type="hidden" id="editTaskId" value="${taskId}">
                        <div class="form-group">
                            <label for="editTaskTitle">Title:</label>
                            <input type="text" id="editTaskTitle" value="${task.title.replace(/"/g, '&quot;')}" required>
                        </div>
                        <div class="form-group">
                            <label for="editTaskDescription">Description:</label>
                            <textarea id="editTaskDescription">${task.description ? task.description.replace(/"/g, '&quot;') : ''}</textarea>
                        </div>
                        <button type="submit">Update Task</button>
                    </form>
                </div>
            `;

            document.body.appendChild(modal);

            // Close button event
            modal.querySelector('.close-modal').addEventListener('click', function() {
                document.body.removeChild(modal);
            });

            // Form submission
            modal.querySelector('#editTaskForm').addEventListener('submit', async function(e) {
                e.preventDefault();

                const updatedTitle = document.getElementById('editTaskTitle').value;
                const updatedDescription = document.getElementById('editTaskDescription').value;

                try {
                    const updateResponse = await fetch(`/api/tasks/${taskId}`, {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            title: updatedTitle,
                            description: updatedDescription
                        })
                    });

                    const updateResult = await updateResponse.json();

                    if (updateResponse.ok) {
                        showSuccess('Task updated successfully!');
                        document.body.removeChild(modal);
                        // Reload tasks to show updated information
                        const userId = document.getElementById('filterUserId').value || document.getElementById('userId').value;
                        await loadTasks(userId);
                    } else {
                        showError(updateResult.detail || 'Failed to update task');
                    }
                } catch (error) {
                    showError(`Error updating task: ${error.message}`);
                }
            });

            // Close modal when clicking outside of it
            modal.addEventListener('click', function(event) {
                if (event.target === modal) {
                    document.body.removeChild(modal);
                }
            });
        } catch (error) {
            showError(`Error loading task for editing: ${error.message}`);
        } finally {
            showLoading(false);
        }
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

    // The old token/model functions have been replaced with the new config functions
    // All functionality is now handled through the config section

    // Check configuration status on page load
    async function checkConfigStatus() {
        try {
            const response = await fetch('/api/config');
            const config = await response.json();

            if (config.status === 'success') {
                configStatusDiv.innerHTML = `
                    <div class="config-status-container config-status-valid">
                        <strong>Provider URL:</strong> ${config.provider_url}<br>
                        <strong>Current Model:</strong> ${config.model}<br>
                        <strong>Token Status:</strong> ${config.has_valid_token ? 'Valid' : 'Invalid/Not Set'}
                    </div>
                `;
            } else {
                configStatusDiv.innerHTML = `
                    <div class="config-status-container config-status-invalid">
                        <strong>Error:</strong> Could not retrieve configuration
                    </div>
                `;
            }
        } catch (error) {
            configStatusDiv.innerHTML = `
                <div class="config-status-container config-status-invalid">
                    <strong>Error:</strong> Could not connect to API (${error.message})
                </div>
            `;
        }
    }

    // Update configuration button click handler
    updateConfigBtn.addEventListener('click', async function() {
        const providerUrl = providerUrlInput.value.trim();
        const apiToken = apiTokenInput.value.trim();
        const modelName = modelNameInput.value.trim();

        if (!providerUrl || !apiToken || !modelName) {
            showError('Provider URL, API token, and model name are all required');
            return;
        }

        try {
            showLoading(true);
            const response = await fetch('/api/update-config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    provider_url: providerUrl,
                    api_token: apiToken,
                    model_name: modelName
                })
            });

            const result = await response.json();

            if (result.status === 'success') {
                showSuccess(result.message);
                // Refresh config status after successful update
                setTimeout(checkConfigStatus, 1000);
                // Clear the inputs
                providerUrlInput.value = '';
                apiTokenInput.value = '';
                modelNameInput.value = '';
            } else {
                showError(result.message || 'Failed to update configuration');
            }
        } catch (error) {
            showError(`Error updating configuration: ${error.message}`);
        } finally {
            showLoading(false);
        }
    });

    // Check configuration button click handler
    checkConfigBtn.addEventListener('click', async function() {
        const providerUrl = providerUrlInput.value.trim();
        const apiToken = apiTokenInput.value.trim();
        const modelName = modelNameInput.value.trim();

        if (!providerUrl || !apiToken || !modelName) {
            showError('Please enter provider URL, API token, and model name to validate');
            return;
        }

        try {
            showLoading(true);
            // Use the backend's health check endpoint to validate the configuration
            const params = new URLSearchParams({
                provider_url: providerUrl,
                api_token: apiToken,
                model_name: modelName
            });

            const response = await fetch(`/api/health?${params}`);
            const result = await response.json();

            if (result.status === 'healthy') {
                showSuccess(`Configuration is valid! Provider: ${result.model || modelName}`);
            } else {
                showError(`Configuration error: ${result.message}`);
            }
        } catch (error) {
            showError(`Error validating configuration: ${error.message}`);
        } finally {
            showLoading(false);
        }
    });

    // Initialize configuration status check
    checkConfigStatus();
});