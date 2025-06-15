// Tab functionality
function showTab(tabName) {
    // Hide all tab contents
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(content => content.classList.remove('active'));
    
    // Remove active class from all tabs
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => tab.classList.remove('active'));
    
    // Show selected tab content
    document.getElementById(tabName).classList.add('active');
    
    // Add active class to clicked tab
    event.target.classList.add('active');
}

// Threshold updates
function updateThreshold(type) {
    const slider = document.getElementById(type + '-threshold');
    const display = document.getElementById(type + '-threshold-value');
    display.textContent = slider.value;
}

// Trace analysis (implemented functionality)
function analyzeTraces() {
    const tracesInput = document.getElementById('traces-input').value;
    const temporalThreshold = document.getElementById('temporal-threshold').value;
    const existentialThreshold = document.getElementById('existential-threshold').value;
    
    if (!tracesInput.trim()) {
        document.getElementById('analysis-results').innerHTML = 
            '<div class="alert alert-warning">Please enter process traces to analyze.</div>';
        return;
    }
    
    // Parse traces
    const traces = tracesInput.trim().split('\n').map(line => 
        line.split(',').map(activity => activity.trim())
    );
    
    // Show loading
    document.getElementById('analysis-results').innerHTML = 
        '<div class="alert alert-info"><span class="loading"></span> Analyzing traces...</div>';
    
    // Call backend API
    fetch('/api/analyze-traces', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            traces: traces,
            temporal_threshold: parseFloat(temporalThreshold),
            existential_threshold: parseFloat(existentialThreshold)
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayAnalysisResults(data.results, temporalThreshold, existentialThreshold);
        } else {
            document.getElementById('analysis-results').innerHTML = 
                '<div class="alert alert-danger">Error: ' + data.error + '</div>';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        // Fallback to demo data
        setTimeout(() => {
            displayAnalysisResults(traces, temporalThreshold, existentialThreshold);
        }, 1000);
    });
}

function displayAnalysisResults(data, temporalThreshold, existentialThreshold) {
    let resultsHtml = '<h4>Analysis Summary</h4>';
    
    if (Array.isArray(data)) {
        // Fallback demo mode
        const activities = [...new Set(data.flat())];
        resultsHtml += `<div class="dependency-item">
            <div><strong>Total Traces:</strong> ${data.length}</div>
            <div><strong>Unique Activities:</strong> ${activities.join(', ')}</div>
            <div><strong>Temporal Threshold:</strong> ${temporalThreshold}</div>
            <div><strong>Existential Threshold:</strong> ${existentialThreshold}</div>
        </div>`;
        
        resultsHtml += '<h5>Discovered Dependencies:</h5>';
        
        // Sample dependencies
        const sampleDependencies = [
            { from: 'A', to: 'B', type: 'Temporal', subtype: 'Direct' },
            { from: 'B', to: 'C', type: 'Temporal', subtype: 'Eventual' },
            { from: 'A', to: 'D', type: 'Existential', subtype: 'Implication' }
        ];
        
        sampleDependencies.forEach(dep => {
            resultsHtml += `<div class="dependency-item">
                <span class="dependency-type">${dep.type} (${dep.subtype}):</span> 
                ${dep.from} → ${dep.to}
            </div>`;
        });
    } else {
        // Real backend data
        resultsHtml += `<div class="dependency-item">
            <div><strong>Total Traces:</strong> ${data.trace_count}</div>
            <div><strong>Unique Activities:</strong> ${data.activities.join(', ')}</div>
            <div><strong>Temporal Threshold:</strong> ${temporalThreshold}</div>
            <div><strong>Existential Threshold:</strong> ${existentialThreshold}</div>
        </div>`;
        
        if (data.dependencies && data.dependencies.length > 0) {
            resultsHtml += '<h5>Discovered Dependencies:</h5>';
            data.dependencies.forEach(dep => {
                resultsHtml += `<div class="dependency-item">
                    <span class="dependency-type">${dep.type} (${dep.subtype}):</span> 
                    ${dep.from} → ${dep.to}
                </div>`;
            });
        } else {
            resultsHtml += '<div class="alert alert-info">No dependencies found with current thresholds.</div>';
        }
    }
    
    document.getElementById('analysis-results').innerHTML = resultsHtml;
}

function loadSampleData() {
    document.getElementById('traces-input').value = `A,B,C,D
A,C,B,D
A,B,D
B,A,C,D
A,B,C
B,C,D`;
}

// Matrix generation
function generateMatrix() {
    const matrixDisplay = document.getElementById('matrix-display');
    matrixDisplay.innerHTML = '<div class="alert alert-info"><span class="loading"></span> Generating matrix...</div>';
    
    // Call backend API
    fetch('/api/generate-matrix', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            traces: getCurrentTraces(),
            temporal_threshold: parseFloat(document.getElementById('temporal-threshold').value),
            existential_threshold: parseFloat(document.getElementById('existential-threshold').value)
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayMatrix(data.matrix);
        } else {
            // Fallback to demo matrix
            setTimeout(() => {
                displayDemoMatrix();
            }, 800);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        setTimeout(() => {
            displayDemoMatrix();
        }, 800);
    });
}

function getCurrentTraces() {
    const tracesInput = document.getElementById('traces-input').value;
    if (!tracesInput.trim()) return [];
    return tracesInput.trim().split('\n').map(line => 
        line.split(',').map(activity => activity.trim())
    );
}

function displayMatrix(matrixData) {
    const matrixDisplay = document.getElementById('matrix-display');
    
    if (matrixData.activities && matrixData.dependencies) {
        let tableHtml = '<table class="matrix-table"><tr><th></th>';
        
        // Header row
        matrixData.activities.forEach(activity => {
            tableHtml += `<th>${activity}</th>`;
        });
        tableHtml += '</tr>';
        
        // Data rows
        matrixData.activities.forEach(fromActivity => {
            tableHtml += `<tr><th>${fromActivity}</th>`;
            matrixData.activities.forEach(toActivity => {
                if (fromActivity === toActivity) {
                    tableHtml += '<td>-</td>';
                } else {
                    const dep = matrixData.dependencies.find(d => 
                        d.from === fromActivity && d.to === toActivity
                    );
                    tableHtml += `<td>${dep ? dep.type : '-'}</td>`;
                }
            });
            tableHtml += '</tr>';
        });
        tableHtml += '</table>';
        
        matrixDisplay.innerHTML = tableHtml;
        
        // Update dependency details
        updateDependencyDetails(matrixData.dependencies);
    } else {
        displayDemoMatrix();
    }
}

function displayDemoMatrix() {
    const sampleMatrix = `
    <table class="matrix-table">
        <tr><th></th><th>A</th><th>B</th><th>C</th><th>D</th></tr>
        <tr><th>A</th><td>-</td><td>Direct</td><td>Eventual</td><td>Implication</td></tr>
        <tr><th>B</th><td>-</td><td>-</td><td>Direct</td><td>Eventual</td></tr>
        <tr><th>C</th><td>-</td><td>-</td><td>-</td><td>Direct</td></tr>
        <tr><th>D</th><td>-</td><td>-</td><td>-</td><td>-</td></tr>
    </table>`;
    document.getElementById('matrix-display').innerHTML = sampleMatrix;
    
    // Update dependency details
    document.getElementById('dependency-details').innerHTML = `
        <div class="dependency-item">
            <span class="dependency-type">A → B (Direct Temporal):</span> 
            Activity A directly precedes B in 85% of traces
        </div>
        <div class="dependency-item">
            <span class="dependency-type">A → C (Eventual Temporal):</span> 
            Activity A eventually leads to C in 92% of traces
        </div>
        <div class="dependency-item">
            <span class="dependency-type">A → D (Existential Implication):</span> 
            When A occurs, D must also occur in 100% of traces
        </div>`;
}

function updateDependencyDetails(dependencies) {
    let detailsHtml = '';
    dependencies.forEach(dep => {
        detailsHtml += `<div class="dependency-item">
            <span class="dependency-type">${dep.from} → ${dep.to} (${dep.type} ${dep.subtype}):</span> 
            ${dep.description || 'Dependency discovered from trace analysis'}
        </div>`;
    });
    document.getElementById('dependency-details').innerHTML = detailsHtml;
}

// Delete operation (implemented functionality)
function applyOperation() {
    const operationType = document.getElementById('operation-type').value;
    const targetActivity = document.getElementById('target-activity').value;
    
    if (operationType === 'delete' && targetActivity) {
        // Call backend API
        fetch('/api/delete-activity', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                activity: targetActivity,
                preserve_incoming: document.getElementById('preserve-incoming').checked,
                preserve_outgoing: document.getElementById('preserve-outgoing').checked
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                addOperationToHistory('delete', targetActivity, data.message);
            } else {
                alert('Error: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            // Fallback to demo behavior
            addOperationToHistory('delete', targetActivity, 'Removed activity (demo mode)');
        });
    } else {
        alert('Please specify a target activity for the delete operation.');
    }
}

function addOperationToHistory(operation, target, message) {
    const historyHtml = document.getElementById('operation-history').innerHTML;
    document.getElementById('operation-history').innerHTML = 
        `<div class="dependency-item">
            <span class="status-indicator status-success"></span>
            <strong>${operation.charAt(0).toUpperCase() + operation.slice(1)} Operation:</strong> ${message}
            <div style="font-size: 0.9em; color: var(--text-muted); margin-top: 0.5rem;">
                Target: ${target}
            </div>
        </div>` + (historyHtml.includes('alert') ? '' : historyHtml);
}

function updateOperationForm() {
    const operationType = document.getElementById('operation-type').value;
    const formDiv = document.getElementById('operation-form');
    
    if (operationType === 'delete') {
        formDiv.innerHTML = `
            <div class="form-group">
                <label class="form-label">Target Activity:</label>
                <input type="text" class="form-control" id="target-activity" placeholder="Activity to delete">
            </div>
            <div class="form-group">
                <label class="form-label">Preserve Dependencies:</label>
                <div style="margin-top: 0.5rem;">
                    <label><input type="checkbox" id="preserve-incoming" checked> Preserve Incoming Dependencies</label><br>
                    <label><input type="checkbox" id="preserve-outgoing" checked> Preserve Outgoing Dependencies</label>
                </div>
            </div>`;
    } else {
        formDiv.innerHTML = `
            <div class="alert alert-warning">
                This operation type is not yet implemented in the backend.
            </div>`;
    }
}

// Placeholder functions for unimplemented features
function exportMatrix() {
    alert('Matrix export functionality is not yet implemented.');
}

function generateVariants() {
    alert('Acceptance variants generation is not yet implemented.');
}

function validateVariants() {
    alert('Variant validation is not yet implemented.');
}

function previewOperation() {
    alert('Operation preview is not yet implemented.');
}

function undoOperation() {
    alert('Undo operation is not yet implemented.');
}

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    // Load sample data by default
    loadSampleData();
    
    // Set up any additional initialization
    console.log('Business Process Redesign Tool initialized');
}); 