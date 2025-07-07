function processInput() {
    const tracesInput = document.getElementById('traces-input').value;
    const yamlFile = document.getElementById('yaml-file').files[0];
    const matrixDisplay = document.getElementById('matrix-display');

    matrixDisplay.innerHTML = '<div class="alert alert-info"><span class="loading"></span> Processing...</div>';

    let fetchOptions;

    if (yamlFile) {
        const formData = new FormData();
        formData.append('file', yamlFile);
        fetchOptions = {
            method: 'POST',
            body: formData
        };
    } else if (tracesInput.trim()) {
        const traces = tracesInput.trim().split('\n').map(line => 
            line.split(',').map(activity => activity.trim())
        );
        fetchOptions = {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ traces: traces })
        };
    } else {
        matrixDisplay.innerHTML = '<div class="alert alert-warning">Please provide traces or upload a YAML file.</div>';
        return;
    }

    fetch('/api/process', fetchOptions)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                fetchAndDisplayMatrix();
            } else {
                matrixDisplay.innerHTML = `<div class="alert alert-danger">Error: ${data.error}</div>`;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            matrixDisplay.innerHTML = '<div class="alert alert-danger">An unexpected error occurred.</div>';
        });
}

function fetchAndDisplayMatrix() {
    const matrixDisplay = document.getElementById('matrix-display');
    matrixDisplay.innerHTML = '<div class="alert alert-info"><span class="loading"></span> Fetching matrix...</div>';

    fetch('/api/matrix')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayMatrix(data, 'matrix-display');
                displayMatrix(data, 'original-matrix-display');
                document.getElementById('modified-matrix-display').innerHTML = '<div class="alert alert-info">The result of the operation will be displayed here.</div>';
            } else {
                document.getElementById('matrix-display').innerHTML = `<div class="alert alert-danger">Error: ${data.error}</div>`;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('matrix-display').innerHTML = '<div class="alert alert-danger">Failed to fetch the matrix.</div>';
        });
}

function displayMatrix(data, elementId) {
    const matrixDisplay = document.getElementById(elementId);
    const activities = data.activities;
    const matrix = data.matrix;

    let tableHtml = '<table class="matrix-table"><tr><th></th>';
    
    activities.forEach(activity => {
        tableHtml += `<th>${activity}</th>`;
    });
    tableHtml += '</tr>';

    activities.forEach(fromActivity => {
        tableHtml += `<tr><th>${fromActivity}</th>`;
        activities.forEach(toActivity => {
            tableHtml += `<td>${matrix[fromActivity][toActivity] || ''}</td>`;
        });
        tableHtml += '</tr>';
    });

    tableHtml += '</table>';
    matrixDisplay.innerHTML = tableHtml;
}

function updateOperationInputs() {
    const operation = document.getElementById('change-operation-select').value;
    const inputsDiv = document.getElementById('operation-inputs');
    inputsDiv.innerHTML = '';

    switch (operation) {
        case 'delete':
            inputsDiv.innerHTML = `
                <div class="form-group">
                    <label class="form-label" for="activity">Activity to Delete:</label>
                    <input type="text" id="activity" class="form-control">
                </div>`;
            break;
        case 'collapse':
            inputsDiv.innerHTML = `
                <div class="form-group">
                    <label class="form-label" for="collapsed_activity">New Collapsed Activity Name:</label>
                    <input type="text" id="collapsed_activity" class="form-control">
                </div>
                <div class="form-group">
                    <label class="form-label" for="collapse_activities">Activities to Collapse (comma-separated):</label>
                    <input type="text" id="collapse_activities" class="form-control">
                </div>`;
            break;
        case 'de-collapse':
            inputsDiv.innerHTML = `
                <div class="form-group">
                    <label class="form-label" for="collapsed_activity">Activity to De-collapse:</label>
                    <input type="text" id="collapsed_activity" class="form-control">
                </div>
                <div class="form-group">
                    <label class="form-label" for="collapsed_matrix_file">Collapsed Matrix (YAML):</label>
                    <input type="file" id="collapsed_matrix_file" class="form-control" accept=".yaml,.yml">
                </div>`;
            break;
        case 'replace':
            inputsDiv.innerHTML = `
                <div class="form-group">
                    <label class="form-label" for="old_activity">Activity to Replace:</label>
                    <input type="text" id="old_activity" class="form-control">
                </div>
                <div class="form-group">
                    <label class="form-label" for="new_activity">New Activity:</label>
                    <input type="text" id="new_activity" class="form-control">
                </div>`;
            break;
        case 'skip':
            inputsDiv.innerHTML = `
                <div class="form-group">
                    <label class="form-label" for="activity_to_skip">Activity to Skip:</label>
                    <input type="text" id="activity_to_skip" class="form-control">
                </div>`;
            break;
        case 'swap':
            inputsDiv.innerHTML = `
                <div class="form-group">
                    <label class="form-label" for="activity1">Activity 1:</label>
                    <input type="text" id="activity1" class="form-control">
                </div>
                <div class="form-group">
                    <label class="form-label" for="activity2">Activity 2:</label>
                    <input type="text" id="activity2" class="form-control">
                </div>`;
            break;
    }
}

function performChangeOperation() {
    const operation = document.getElementById('change-operation-select').value;
    const formData = new FormData();
    formData.append('operation', operation);

    switch (operation) {
        case 'delete':
            formData.append('activity', document.getElementById('activity').value);
            break;
        case 'collapse':
            formData.append('collapsed_activity', document.getElementById('collapsed_activity').value);
            formData.append('collapse_activities', document.getElementById('collapse_activities').value.split(',').map(s => s.trim()));
            break;
        case 'de-collapse':
            formData.append('collapsed_activity', document.getElementById('collapsed_activity').value);
            formData.append('collapsed_matrix_file', document.getElementById('collapsed_matrix_file').files[0]);
            break;
        case 'replace':
            formData.append('old_activity', document.getElementById('old_activity').value);
            formData.append('new_activity', document.getElementById('new_activity').value);
            break;
        case 'skip':
            formData.append('activity_to_skip', document.getElementById('activity_to_skip').value);
            break;
        case 'swap':
            formData.append('activity1', document.getElementById('activity1').value);
            formData.append('activity2', document.getElementById('activity2').value);
            break;
    }

    const modifiedMatrixDisplay = document.getElementById('modified-matrix-display');
    modifiedMatrixDisplay.innerHTML = '<div class="alert alert-info"><span class="loading"></span> Performing operation...</div>';

    fetch('/api/change', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayMatrix(data, 'modified-matrix-display');
        } else {
            modifiedMatrixDisplay.innerHTML = `<div class="alert alert-danger">Error: ${data.error}</div>`;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        modifiedMatrixDisplay.innerHTML = '<div class="alert alert-danger">An unexpected error occurred.</div>';
    });
}


// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('change-operation-select').addEventListener('change', updateOperationInputs);
    console.log('Business Process Redesign Tool initialized');
});