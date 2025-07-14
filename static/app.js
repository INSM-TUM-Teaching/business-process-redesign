// Global variables to store matrix data
let originalMatrixData = null;
let modifiedMatrixData = null;

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
                originalMatrixData = data;
                modifiedMatrixData = null; // Clear any previous modified matrix
                
                displayMatrix(data, 'matrix-display');
                displayMatrix(data, 'original-matrix-display');
                document.getElementById('modified-matrix-display').innerHTML = '<div class="alert alert-info">The result of the operation will be displayed here.</div>';
                
                // Reset matrix source selection to "original" and disable "modified" option
                const matrixSourceSelect = document.getElementById('matrix-source-select');
                matrixSourceSelect.value = 'original';
                const modifiedOption = document.querySelector('#matrix-source-select option[value="modified"]');
                modifiedOption.disabled = true;
                modifiedOption.textContent = 'Modified Matrix';
                updateMatrixSourceTitle();
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
    const cellClasses = data.cell_classes || {};

    let tableHtml = '<table class="matrix-table"><tr><th></th>';
    
    activities.forEach(activity => {
        let headerClass = '';
        if (data.diff_info) {
            if (data.diff_info.added_activities && data.diff_info.added_activities.includes(activity)) {
                headerClass = 'diff-added-activity';
            } else if (data.diff_info.removed_activities && data.diff_info.removed_activities.includes(activity)) {
                headerClass = 'diff-removed-activity';
            }
        }
        tableHtml += `<th class="${headerClass}">${activity}</th>`;
    });
    tableHtml += '</tr>';

    activities.forEach(fromActivity => {
        let rowHeaderClass = '';
        if (data.diff_info) {
            if (data.diff_info.added_activities && data.diff_info.added_activities.includes(fromActivity)) {
                rowHeaderClass = 'diff-added-activity';
            } else if (data.diff_info.removed_activities && data.diff_info.removed_activities.includes(fromActivity)) {
                rowHeaderClass = 'diff-removed-activity';
            }
        }
        tableHtml += `<tr><th class="${rowHeaderClass}">${fromActivity}</th>`;
        
        activities.forEach(toActivity => {
            const cellClass = cellClasses[fromActivity] ? cellClasses[fromActivity][toActivity] || '' : '';
            tableHtml += `<td class="${cellClass}">${matrix[fromActivity][toActivity] || ''}</td>`;
        });
        tableHtml += '</tr>';
    });

    tableHtml += '</table>';
    
    if (data.diff_info && (data.diff_info.added_activities.length > 0 || 
                          data.diff_info.removed_activities.length > 0 || 
                          data.diff_info.modified_cells.length > 0)) {
        tableHtml += createDiffLegend(data.diff_info);
    }
    
    matrixDisplay.innerHTML = tableHtml;
}

function createDiffLegend(diffInfo) {
    let legendHtml = '<div class="diff-legend">';
    
    if (diffInfo.added_activities.length > 0) {
        legendHtml += `
            <div class="diff-legend-item">
                <div class="diff-legend-color added-activity"></div>
                <span>Added Activities (${diffInfo.added_activities.length})</span>
            </div>`;
    }
    
    if (diffInfo.removed_activities.length > 0) {
        legendHtml += `
            <div class="diff-legend-item">
                <div class="diff-legend-color removed-activity"></div>
                <span>Removed Activities (${diffInfo.removed_activities.length})</span>
            </div>`;
    }
    
    if (diffInfo.added_cells.length > 0) {
        legendHtml += `
            <div class="diff-legend-item">
                <div class="diff-legend-color added"></div>
                <span>Added Dependencies</span>
            </div>`;
    }
    
    if (diffInfo.removed_cells.length > 0) {
        legendHtml += `
            <div class="diff-legend-item">
                <div class="diff-legend-color removed"></div>
                <span>Removed Dependencies</span>
            </div>`;
    }
    
    if (diffInfo.modified_cells.length > 0) {
        legendHtml += `
            <div class="diff-legend-item">
                <div class="diff-legend-color modified"></div>
                <span>Modified Dependencies (${diffInfo.modified_cells.length})</span>
            </div>`;
    }
    
    legendHtml += '</div>';
    return legendHtml;
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
        case 'insert':
            inputsDiv.innerHTML = `
                <div class="form-group">
                    <label class="form-label" for="activity">Activity to Insert:</label>
                    <input type="text" id="activity" class="form-control">
                </div>
                <div class="form-group">
                    <label class="form-label">Dependencies for the new activity:</label>
                    <div id="dependencies-container">
                        <!-- Dependencies will be added here -->
                    </div>
                    <button type="button" class="btn btn-secondary" onclick="addDependency()">Add Dependency</button>
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
        case 'modify':
            inputsDiv.innerHTML = `
                <div class="form-group">
                    <label class="form-label" for="from_activity">From Activity:</label>
                    <input type="text" id="from_activity" class="form-control">
                </div>
                <div class="form-group">
                    <label class="form-label" for="to_activity">To Activity:</label>
                    <input type="text" id="to_activity" class="form-control">
                </div>
                <div class="form-group">
                    <label class="form-label" for="temporal_dep">Temporal Dependency:</label>
                    <select id="temporal_dep" class="form-control">
                        <option value="">--No Change--</option>
                        <option value="DIRECT">Direct</option>
                        <option value="EVENTUAL">Eventual</option>
                        <option value="INDEPENDENCE">Independence</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label" for="temporal_direction">Temporal Direction:</label>
                    <select id="temporal_direction" class="form-control">
                        <option value="FORWARD">Forward</option>
                        <option value="BACKWARD">Backward</option>
                        <option value="BOTH">Both</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label" for="existential_dep">Existential Dependency:</label>
                    <select id="existential_dep" class="form-control">
                        <option value="">--No Change--</option>
                        <option value="IMPLICATION">Implication</option>
                        <option value="EQUIVALENCE">Equivalence</option>
                        <option value="NEGATED_EQUIVALENCE">Negated Equivalence</option>
                        <option value="NAND">NAND</option>
                        <option value="OR">OR</option>
                        <option value="INDEPENDENCE">Independence</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label" for="existential_direction">Existential Direction:</label>
                    <select id="existential_direction" class="form-control">
                        <option value="FORWARD">Forward</option>
                        <option value="BACKWARD">Backward</option>
                        <option value="BOTH">Both</option>
                    </select>
                </div>`;
            
            setTimeout(() => {
                const bothDirectionTypes = ['EQUIVALENCE', 'NEGATED_EQUIVALENCE', 'NAND', 'OR', 'INDEPENDENCE'];
                
                const temporalDepSelect = document.getElementById('temporal_dep');
                const existentialDepSelect = document.getElementById('existential_dep');
                const temporalDirectionSelect = document.getElementById('temporal_direction');
                const existentialDirectionSelect = document.getElementById('existential_direction');

                temporalDepSelect.addEventListener('change', (e) => {
                    if (bothDirectionTypes.includes(e.target.value)) {
                        temporalDirectionSelect.value = 'BOTH';
                    } else if (e.target.value !== '') {
                        temporalDirectionSelect.value = 'FORWARD';
                    }
                });

                existentialDepSelect.addEventListener('change', (e) => {
                    if (bothDirectionTypes.includes(e.target.value)) {
                        existentialDirectionSelect.value = 'BOTH';
                    } else if (e.target.value !== '') {
                        existentialDirectionSelect.value = 'FORWARD';
                    }
                });
                
                if (bothDirectionTypes.includes(existentialDepSelect.value)) {
                    existentialDirectionSelect.value = 'BOTH';
                }
            }, 0);
            break;
    }
}

let dependencyCounter = 0;

function addDependency() {
    const container = document.getElementById('dependencies-container');
    const dependencyId = dependencyCounter++;
    
    const dependencyDiv = document.createElement('div');
    dependencyDiv.className = 'dependency-item';
    dependencyDiv.style.border = '1px solid #ddd';
    dependencyDiv.style.padding = '10px';
    dependencyDiv.style.margin = '5px 0';
    dependencyDiv.style.borderRadius = '4px';
    
    dependencyDiv.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <strong>Dependency ${dependencyId + 1}</strong>
            <button type="button" class="btn btn-danger btn-sm" onclick="removeDependency(this)">Remove</button>
        </div>
        <div class="form-group">
            <label class="form-label">From Activity:</label>
            <input type="text" name="from_activity_${dependencyId}" class="form-control" placeholder="Activity name">
        </div>
        <div class="form-group">
            <label class="form-label">To Activity:</label>
            <input type="text" name="to_activity_${dependencyId}" class="form-control" placeholder="Activity name">
        </div>
        <div class="form-group">
            <label class="form-label">Temporal Dependency:</label>
            <select name="temporal_dep_${dependencyId}" class="form-control temporal-dependency-select">
                <option value="">--None--</option>
                <option value="DIRECT">Direct</option>
                <option value="EVENTUAL">Eventual</option>
                <option value="INDEPENDENCE">Independence</option>
            </select>
        </div>
        <div class="form-group">
            <label class="form-label">Temporal Direction:</label>
            <select name="temporal_direction_${dependencyId}" class="form-control temporal-direction-select">
                <option value="FORWARD">Forward</option>
                <option value="BACKWARD">Backward</option>
                <option value="BOTH">Both</option>
            </select>
        </div>
        <div class="form-group">
            <label class="form-label">Existential Dependency:</label>
            <select name="existential_dep_${dependencyId}" class="form-control existential-dependency-select">
                <option value="">--None--</option>
                <option value="IMPLICATION">Implication</option>
                <option value="EQUIVALENCE">Equivalence</option>
                <option value="NEGATED_EQUIVALENCE">Negated Equivalence</option>
                <option value="NAND">NAND</option>
                <option value="OR">OR</option>
                <option value="INDEPENDENCE">Independence</option>
            </select>
        </div>
        <div class="form-group">
            <label class="form-label">Existential Direction:</label>
            <select name="existential_direction_${dependencyId}" class="form-control existential-direction-select">
                <option value="FORWARD">Forward</option>
                <option value="BACKWARD">Backward</option>
                <option value="BOTH">Both</option>
            </select>
        </div>
    `;
    
    container.appendChild(dependencyDiv);
    
    // Add event listeners for direction defaults based on dependency types
    const bothDirectionTypes = ['EQUIVALENCE', 'NEGATED_EQUIVALENCE', 'NAND', 'OR', 'INDEPENDENCE'];
    
    const temporalDepSelect = dependencyDiv.querySelector('.temporal-dependency-select');
    const temporalDirectionSelect = dependencyDiv.querySelector('.temporal-direction-select');
    const existentialDepSelect = dependencyDiv.querySelector('.existential-dependency-select');
    const existentialDirectionSelect = dependencyDiv.querySelector('.existential-direction-select');
    
    temporalDepSelect.addEventListener('change', (e) => {
        if (bothDirectionTypes.includes(e.target.value)) {
            temporalDirectionSelect.value = 'BOTH';
        } else if (e.target.value !== '') {
            temporalDirectionSelect.value = 'FORWARD';
        }
    });

    existentialDepSelect.addEventListener('change', (e) => {
        if (bothDirectionTypes.includes(e.target.value)) {
            existentialDirectionSelect.value = 'BOTH';
        } else if (e.target.value !== '') {
            existentialDirectionSelect.value = 'FORWARD';
        }
    });
}

function removeDependency(button) {
    const dependencyDiv = button.closest('.dependency-item');
    dependencyDiv.remove();
}

function performChangeOperation() {
    const operation = document.getElementById('change-operation-select').value;
    const matrixSource = document.getElementById('matrix-source-select').value;
    const formData = new FormData();
    formData.append('operation', operation);
    formData.append('matrix_source', matrixSource);

    switch (operation) {
        case 'delete':
            formData.append('activity', document.getElementById('activity').value);
            break;
        case 'insert':
            formData.append('activity', document.getElementById('activity').value);
            
            // Count dependencies and add them to form data
            const dependencyItems = document.querySelectorAll('.dependency-item');
            formData.append('dependency_count', dependencyItems.length);
            
            dependencyItems.forEach((item, index) => {
                const fromActivity = item.querySelector(`input[name^="from_activity_"]`).value;
                const toActivity = item.querySelector(`input[name^="to_activity_"]`).value;
                const temporalDep = item.querySelector(`select[name^="temporal_dep_"]`).value;
                const temporalDirection = item.querySelector(`select[name^="temporal_direction_"]`).value;
                const existentialDep = item.querySelector(`select[name^="existential_dep_"]`).value;
                const existentialDirection = item.querySelector(`select[name^="existential_direction_"]`).value;
                
                formData.append(`from_activity_${index}`, fromActivity);
                formData.append(`to_activity_${index}`, toActivity);
                formData.append(`temporal_dep_${index}`, temporalDep);
                formData.append(`temporal_direction_${index}`, temporalDirection);
                formData.append(`existential_dep_${index}`, existentialDep);
                formData.append(`existential_direction_${index}`, existentialDirection);
            });
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
        case 'modify':
            formData.append('from_activity', document.getElementById('from_activity').value);
            formData.append('to_activity', document.getElementById('to_activity').value);
            
            const temporalDep = document.getElementById('temporal_dep').value;
            const existentialDep = document.getElementById('existential_dep').value;
            const temporalDirection = document.getElementById('temporal_direction').value;
            const existentialDirection = document.getElementById('existential_direction').value;
            
            if (temporalDep) {
                formData.append('temporal_dep', temporalDep);
                formData.append('temporal_direction', temporalDirection);
            }
            if (existentialDep) {
                formData.append('existential_dep', existentialDep);
                formData.append('existential_direction', existentialDirection);
            }
            break;
    }

    const originalMatrixDisplay = document.getElementById('original-matrix-display');
    const modifiedMatrixDisplay = document.getElementById('modified-matrix-display');
    
    document.getElementById('export-button').style.display = 'none';
    
    originalMatrixDisplay.innerHTML = '<div class="alert alert-info"><span class="loading"></span> Performing operation...</div>';
    modifiedMatrixDisplay.innerHTML = '<div class="alert alert-info"><span class="loading"></span> Performing operation...</div>';

    fetch('/api/change', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            modifiedMatrixData = data.modified;
            
            displayMatrix(data.original, 'original-matrix-display');
            displayMatrix(data.modified, 'modified-matrix-display');
            console.log('Diff Info:', data.diff_info);
            
            const modifiedOption = document.querySelector('#matrix-source-select option[value="modified"]');
            modifiedOption.disabled = false;
            modifiedOption.textContent = 'Modified Matrix (Available)';
            
            // Update the source matrix display if "modified" is currently selected
            const matrixSource = document.getElementById('matrix-source-select').value;
            if (matrixSource === 'modified') {
                updateSourceMatrixDisplay('modified');
            }
            
            document.getElementById('export-button').style.display = 'inline-block';
        } else {
            originalMatrixDisplay.innerHTML = `<div class="alert alert-danger">Error: ${data.error}</div>`;
            modifiedMatrixDisplay.innerHTML = `<div class="alert alert-danger">Error: ${data.error}</div>`;
            document.getElementById('export-button').style.display = 'none';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        originalMatrixDisplay.innerHTML = '<div class="alert alert-danger">An unexpected error occurred.</div>';
        modifiedMatrixDisplay.innerHTML = '<div class="alert alert-danger">An unexpected error occurred.</div>';
        // Hide export button on error
        document.getElementById('export-button').style.display = 'none';
    });
}

function exportModifiedMatrix() {
    fetch('/api/export')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const blob = new Blob([data.yaml_data], { type: 'application/x-yaml' });
                const url = window.URL.createObjectURL(blob);
                
                const link = document.createElement('a');
                link.href = url;
                link.download = data.filename;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                
                window.URL.revokeObjectURL(url);
            } else {
                alert('Export failed: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while exporting the matrix.');
        });
}

function updateMatrixSourceTitle() {
    const matrixSource = document.getElementById('matrix-source-select').value;
    const titleElement = document.getElementById('source-matrix-title');
    const modifiedOption = document.querySelector('#matrix-source-select option[value="modified"]');
    
    if (matrixSource === 'modified') {
        titleElement.textContent = 'Modified Matrix (Source)';
        if (modifiedOption.disabled) {
            // If modified option is disabled, reset to original
            document.getElementById('matrix-source-select').value = 'original';
            titleElement.textContent = 'Initial Matrix (Source)';
            showMatrixSourceStatus('original');
            updateSourceMatrixDisplay('original');
        } else {
            showMatrixSourceStatus('modified');
            updateSourceMatrixDisplay('modified');
        }
    } else {
        titleElement.textContent = 'Initial Matrix (Source)';
        showMatrixSourceStatus('original');
        updateSourceMatrixDisplay('original');
    }
}

function updateSourceMatrixDisplay(matrixSource) {
    const sourceDisplay = document.getElementById('original-matrix-display');
    
    if (matrixSource === 'modified' && modifiedMatrixData) {
        displayMatrix(modifiedMatrixData, 'original-matrix-display');
    } else if (matrixSource === 'original' && originalMatrixData) {
        displayMatrix(originalMatrixData, 'original-matrix-display');
    } else {
        sourceDisplay.innerHTML = '<div class="alert alert-info">Generate a matrix first to perform operations on it.</div>';
    }
}

function showMatrixSourceStatus(matrixSource) {
    const statusMessages = {
        'original': 'Using Initial Matrix as source for operation',
        'modified': 'Using Modified Matrix as source for operation'
    };
    
    let statusElement = document.getElementById('matrix-source-status');
    if (!statusElement) {
        statusElement = document.createElement('div');
        statusElement.id = 'matrix-source-status';
        statusElement.className = 'alert alert-info';
        statusElement.style.marginTop = '10px';
        statusElement.style.fontSize = '0.9em';
        
        const operationInputs = document.getElementById('operation-inputs');
        if (operationInputs.nextSibling) {
            operationInputs.parentNode.insertBefore(statusElement, operationInputs.nextSibling);
        } else {
            operationInputs.parentNode.appendChild(statusElement);
        }
    }
    
    statusElement.textContent = statusMessages[matrixSource] || '';
    statusElement.style.display = matrixSource ? 'block' : 'none';
}

function updateSourceMatrixDisplay(matrixSource) {
    const originalMatrixDisplay = document.getElementById('original-matrix-display');
    const modifiedMatrixDisplay = document.getElementById('modified-matrix-display');
    
    if (matrixSource === 'original' && originalMatrixData) {
        displayMatrix(originalMatrixData, 'original-matrix-display');
    } else if (matrixSource === 'modified' && modifiedMatrixData) {
        displayMatrix(modifiedMatrixData, 'modified-matrix-display');
    }
}

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('change-operation-select').addEventListener('change', updateOperationInputs);
    document.getElementById('matrix-source-select').addEventListener('change', () => {
        updateMatrixSourceTitle();
        showMatrixSourceStatus(document.getElementById('matrix-source-select').value);
    });
    
    // Initialize the "Modified Matrix" option as disabled
    const modifiedOption = document.querySelector('#matrix-source-select option[value="modified"]');
    modifiedOption.disabled = true;
    updateMatrixSourceTitle();
    
    console.log('Business Process Redesign Tool initialized');
});