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
                displayMatrix(data);
            } else {
                matrixDisplay.innerHTML = `<div class="alert alert-danger">Error: ${data.error}</div>`;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            matrixDisplay.innerHTML = '<div class="alert alert-danger">Failed to fetch the matrix.</div>';
        });
}

function displayMatrix(data) {
    const matrixDisplay = document.getElementById('matrix-display');
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

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    // Set up any additional initialization
    console.log('Business Process Redesign Tool initialized');
});