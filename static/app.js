// Global variables to store dependency data
let originalDependenciesData = null;
let modifiedDependenciesData = null;

let lockedDependencies = [];

function processInput() {
    const tracesInput = document.getElementById('traces-input').value;
    const yamlFile = document.getElementById('yaml-file').files[0];
    const dependenciesDisplay = document.getElementById('dependencies-display');

    dependenciesDisplay.innerHTML = '<div class="alert alert-info"><span class="loading"></span> Processing...</div>';

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
        dependenciesDisplay.innerHTML = '<div class="alert alert-warning">Please provide traces or upload a YAML file.</div>';
        return;
    }

    fetch('/api/process', fetchOptions)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                fetchAndDisplayDependencies();
            } else {
                dependenciesDisplay.innerHTML = `<div class="alert alert-danger">Error: ${data.error}</div>`;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            dependenciesDisplay.innerHTML = '<div class="alert alert-danger">An unexpected error occurred.</div>';
        });
}

function fetchAndDisplayDependencies() {
    const dependenciesDisplay = document.getElementById('dependencies-display');
    dependenciesDisplay.innerHTML = '<div class="alert alert-info"><span class="loading"></span> Analyzing dependencies...</div>';

    fetch('/api/matrix')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                originalDependenciesData = data;
                modifiedDependenciesData = null; // Clear any previous modified dependencies
                
                displayDependencies(data, 'dependencies-display');
                displayDependencies(data, 'original-dependencies-display');
                document.getElementById('modified-dependencies-display').innerHTML = '<div class="alert alert-info">The result of the operation will be displayed here.</div>';
                
                // Reset dependencies source selection to "original" and disable "modified" option
                const dependenciesSourceSelect = document.getElementById('dependencies-source-select');
                dependenciesSourceSelect.value = 'original';
                const modifiedOption = document.querySelector('#dependencies-source-select option[value="modified"]');
                modifiedOption.disabled = true;
                modifiedOption.textContent = 'Modified Dependencies';
                updateDependenciesSourceTitle();
                populateLockSelections(data.activities);
            } else {
                document.getElementById('dependencies-display').innerHTML = `<div class="alert alert-danger">Error: ${data.error}</div>`;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('dependencies-display').innerHTML = '<div class="alert alert-danger">Failed to analyze dependencies.</div>';
        });
}

function displayDependencies(data, elementId) {
    const dependenciesDisplay = document.getElementById(elementId);
    const activities = data.activities;
    const matrix = data.matrix;
    const cellClasses = data.cell_classes || {};

    let dependenciesHtml = '<div class="dependencies-overview">';
    dependenciesHtml += '<h4>Activity Dependencies</h4>';
    dependenciesHtml += '<div class="dependencies-explanation">Below you can see how activities depend on each other in your process:</div>';
    
    // Create a more user-friendly dependency list
    let hasAnyDependencies = false;
    let dependencyList = '<div class="dependency-list">';
    
    activities.forEach(fromActivity => {
        activities.forEach(toActivity => {
            if (fromActivity !== toActivity && matrix[fromActivity] && matrix[fromActivity][toActivity]) {
                const cellContent = matrix[fromActivity][toActivity];
                if (cellContent && cellContent !== '' && cellContent !== '-,-') {
                    hasAnyDependencies = true;
                    
                    let dependencyHtml = '<div class="dependency-item">';
                    dependencyHtml += `<div class="dependency-pair"><strong>${fromActivity}</strong> → <strong>${toActivity}</strong></div>`;
                    
                    // Parse the dependency notation and create user-friendly explanations
                    const explanation = parseDependencyExplanation(cellContent, fromActivity, toActivity);
                    dependencyHtml += `<div class="dependency-explanation">${explanation}</div>`;
                    
                    // Add diff classes if this is a comparison view
                    let itemClass = '';
                    if (data.diff_info) {
                        if (data.diff_info.added_cells && data.diff_info.added_cells.some(cell => cell[0] === fromActivity && cell[1] === toActivity)) {
                            itemClass = 'diff-added';
                        } else if (data.diff_info.removed_cells && data.diff_info.removed_cells.some(cell => cell[0] === fromActivity && cell[1] === toActivity)) {
                            itemClass = 'diff-removed';
                        } else if (data.diff_info.modified_cells && data.diff_info.modified_cells.some(cell => cell[0] === fromActivity && cell[1] === toActivity)) {
                            itemClass = 'diff-modified';
                        }
                    }
                    
                    dependencyHtml += `</div>`;
                    dependencyList += `<div class="dependency-card ${itemClass}">${dependencyHtml}</div>`;
                }
            }
        });
    });
    
    dependencyList += '</div>';
    
    if (!hasAnyDependencies) {
        dependenciesHtml += '<div class="alert alert-info">No specific dependencies found. All activities can be executed in any order.</div>';
    } else {
        dependenciesHtml += dependencyList;
    }
    
    // Add activities list
    dependenciesHtml += '<div class="activities-summary">';
    dependenciesHtml += '<h5>Activities in your process:</h5>';
    dependenciesHtml += '<div class="activities-list">';
    activities.forEach(activity => {
        let activityClass = '';
        if (data.diff_info) {
            if (data.diff_info.added_activities && data.diff_info.added_activities.includes(activity)) {
                activityClass = 'diff-added-activity';
            } else if (data.diff_info.removed_activities && data.diff_info.removed_activities.includes(activity)) {
                activityClass = 'diff-removed-activity';
            }
        }
        dependenciesHtml += `<span class="activity-tag ${activityClass}">${activity}</span>`;
    });
    dependenciesHtml += '</div></div>';
    
    dependenciesHtml += '</div>';
    
    // Add legend if this is a diff view
    if (data.diff_info && (data.diff_info.added_activities.length > 0 || 
                          data.diff_info.removed_activities.length > 0 || 
                          data.diff_info.modified_cells.length > 0)) {
        dependenciesHtml += createDiffLegend(data.diff_info);
    }
    
    dependenciesDisplay.innerHTML = dependenciesHtml;
}

function parseDependencyExplanation(cellContent, fromActivity, toActivity) {
    // Parse the matrix notation and convert to user-friendly explanations
    const parts = cellContent.split(',');
    const temporalPart = parts[0] || '-';
    const existentialPart = parts[1] || '-';
    
    let explanations = [];
    
    // Temporal dependency explanation
    if (temporalPart !== '-') {
        if (temporalPart.includes('≺')) {
            if (temporalPart.includes('d')) {
                explanations.push(`<span class="temporal-dep" title="This means ${fromActivity} must happen immediately before ${toActivity} with no other activities in between">Timing: <strong>${fromActivity}</strong> must happen directly before <strong>${toActivity}</strong></span>`);
            } else {
                explanations.push(`<span class="temporal-dep" title="This means ${fromActivity} must happen before ${toActivity}, but other activities can happen in between">Timing: <strong>${fromActivity}</strong> must happen before <strong>${toActivity}</strong></span>`);
            }
        } else if (temporalPart.includes('≻')) {
            if (temporalPart.includes('d')) {
                explanations.push(`<span class="temporal-dep" title="This means ${toActivity} must happen immediately before ${fromActivity} with no other activities in between">Timing: <strong>${toActivity}</strong> must happen directly before <strong>${fromActivity}</strong></span>`);
            } else {
                explanations.push(`<span class="temporal-dep" title="This means ${toActivity} must happen before ${fromActivity}, but other activities can happen in between">Timing: <strong>${toActivity}</strong> must happen before <strong>${fromActivity}</strong></span>`);
            }
        }
    }
    
    // Existential dependency explanation  
    if (existentialPart !== '-') {
        if (existentialPart === '=>') {
            explanations.push(`<span class="existential-dep" title="If ${fromActivity} occurs in a process instance, then ${toActivity} must also occur in that same instance">Occurrence: If <strong>${fromActivity}</strong> happens, then <strong>${toActivity}</strong> must also happen</span>`);
        } else if (existentialPart === '<=') {
            explanations.push(`<span class="existential-dep" title="If ${toActivity} occurs in a process instance, then ${fromActivity} must also occur in that same instance">Occurrence: If <strong>${toActivity}</strong> happens, then <strong>${fromActivity}</strong> must also happen</span>`);
        } else if (existentialPart === '⇔') {
            explanations.push(`<span class="existential-dep" title="Both activities must always occur together - either both happen or neither happens in any process instance">Occurrence: <strong>${fromActivity}</strong> and <strong>${toActivity}</strong> must both happen or both not happen</span>`);
        } else if (existentialPart === '⇎') {
            explanations.push(`<span class="existential-dep" title="These activities are mutually exclusive - only one can happen in any process instance">Occurrence: Either <strong>${fromActivity}</strong> or <strong>${toActivity}</strong> can happen, but not both</span>`);
        } else if (existentialPart === '∧') {
            explanations.push(`<span class="existential-dep" title="Both activities must occur together in every process instance">Occurrence: Both <strong>${fromActivity}</strong> and <strong>${toActivity}</strong> must happen together</span>`);
        } else if (existentialPart === '⊼') {
            explanations.push(`<span class="existential-dep" title="These activities cannot both occur in the same process instance">Occurrence: <strong>${fromActivity}</strong> and <strong>${toActivity}</strong> cannot both happen</span>`);
        } else if (existentialPart === '∨') {
            explanations.push(`<span class="existential-dep" title="At least one of these activities must occur in every process instance">Occurrence: At least one of <strong>${fromActivity}</strong> or <strong>${toActivity}</strong> must happen</span>`);
        }
    }
    
    if (explanations.length === 0) {
        return `<span class="no-dep" title="These activities have no specific dependency constraints and can occur independently">No specific dependency constraint between these activities</span>`;
    }
    
    return explanations.join('<br>');
}

function createDiffLegend(diffInfo) {
    let legendHtml = '<div class="diff-legend">';
    legendHtml += '<h5 style="color: var(--text-primary); margin-bottom: 1rem;">Changes Overview:</h5>';
    
    if (diffInfo.added_activities.length > 0) {
        legendHtml += `
            <div class="diff-legend-item">
                <div class="diff-legend-color added-activity"></div>
                <span>Added Activities (${diffInfo.added_activities.length}): ${diffInfo.added_activities.join(', ')}</span>
            </div>`;
    }
    
    if (diffInfo.removed_activities.length > 0) {
        legendHtml += `
            <div class="diff-legend-item">
                <div class="diff-legend-color removed-activity"></div>
                <span>Removed Activities (${diffInfo.removed_activities.length}): ${diffInfo.removed_activities.join(', ')}</span>
            </div>`;
    }
    
    if (diffInfo.added_cells && diffInfo.added_cells.length > 0) {
        legendHtml += `
            <div class="diff-legend-item">
                <div class="diff-legend-color added"></div>
                <span>New Dependencies (${diffInfo.added_cells.length})</span>
            </div>`;
    }
    
    if (diffInfo.removed_cells && diffInfo.removed_cells.length > 0) {
        legendHtml += `
            <div class="diff-legend-item">
                <div class="diff-legend-color removed"></div>
                <span>Removed Dependencies (${diffInfo.removed_cells.length})</span>
            </div>`;
    }
    
    if (diffInfo.modified_cells && diffInfo.modified_cells.length > 0) {
        legendHtml += `
            <div class="diff-legend-item">
                <div class="diff-legend-color modified"></div>
                <span>Modified Dependencies (${diffInfo.modified_cells.length})</span>
            </div>`;
    }
    
    legendHtml += '</div>';
    return legendHtml;
}
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
                    <label class="form-label" for="collapsed_dependencies_file">Collapsed Dependencies (YAML):</label>
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
        case 'move':
            inputsDiv.innerHTML = `
                <div class="form-group">
                    <label class="form-label" for="activity">Activity to Move:</label>
                    <input type="text" id="activity" class="form-control">
                </div>
                <div class="form-group">
                    <label class="form-label">New Dependencies for the activity:</label>
                    <div id="dependencies-container">
                        <!-- Dependencies will be added here -->
                    </div>
                    <button type="button" class="btn btn-secondary" onclick="addDependency()">Add Dependency</button>
                </div>`;
            break;
        case 'parallelize':
            inputsDiv.innerHTML = `
                <div class="form-group">
                    <label class="form-label" for="parallel_activities">Activities to Parallelize (comma-separated):</label>
                    <input type="text" id="parallel_activities" class="form-control">
                </div>`;
            break;
        case 'condition_update':
            inputsDiv.innerHTML = `
                <div class="form-group">
                    <label class="form-label" for="condition_activity">Condition Activity:</label>
                    <input type="text" id="condition_activity" class="form-control">
                </div>
                <div class="form-group">
                    <label class="form-label" for="depending_activity">Depending Activity:</label>
                    <input type="text" id="depending_activity" class="form-control">
                </div>`;
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

function populateLockSelections(activities) {
    // Reset locks when new matrix is fetched
    lockedDependencies = [];
    const fromSelect = document.getElementById('lock-from-activity');
    const toSelect = document.getElementById('lock-to-activity');
    fromSelect.innerHTML = '<option value="">From Activity</option>';
    toSelect.innerHTML = '<option value="">To Activity</option>';
    activities.forEach(act => {
        const opt1 = document.createElement('option'); opt1.value = act; opt1.textContent = act;
        const opt2 = document.createElement('option'); opt2.value = act; opt2.textContent = act;
        fromSelect.appendChild(opt1);
        toSelect.appendChild(opt2);
    });
    // Clear existing locks list UI
    renderLocksList();
}

function addLock() {
    const from = document.getElementById('lock-from-activity').value;
    const to = document.getElementById('lock-to-activity').value;
    const temporal = document.getElementById('lock-temporal').checked;
    const existential = document.getElementById('lock-existential').checked;
    if (!from || !to) {
        alert('Please select both From and To activities for locking.'); return;
    }
    if (!temporal && !existential) {
        alert('Please select at least one lock type (Temporal or Existential).'); return;
    }
    lockedDependencies.push({from, to, temporal, existential});
    renderLocksList();
}

function removeLock(index) {
    lockedDependencies.splice(index, 1);
    renderLocksList();
}

function renderLocksList() {
    const list = document.getElementById('locks-list');
    list.innerHTML = '';
    list.className = 'list-group';
    if (lockedDependencies.length === 0) {
        const empty = document.createElement('div');
        empty.className = 'text-muted';
        empty.textContent = 'No locks added.';
        list.appendChild(empty);
        return;
    }
    lockedDependencies.forEach((lock, idx) => {
        const li = document.createElement('li');
        li.className = 'list-group-item d-flex justify-content-between align-items-center';
        const info = document.createElement('div');
        info.innerHTML = `<strong>${lock.from}</strong> → <strong>${lock.to}</strong>
            ${lock.temporal ? '<span class="badge badge-primary badge-pill ml-2">Temporal</span>' : ''}
            ${lock.existential ? '<span class="badge badge-secondary badge-pill ml-2">Existential</span>' : ''}`;
        const btn = document.createElement('button');
        btn.textContent = 'Remove';
        btn.className = 'btn btn-sm btn-outline-danger';
        btn.onclick = () => removeLock(idx);
        li.appendChild(info);
        li.appendChild(btn);
        list.appendChild(li);
    });
}

function performChangeOperation() {
    const operation = document.getElementById('change-operation-select').value;
    const dependenciesSource = document.getElementById('dependencies-source-select').value;
    const formData = new FormData();
    formData.append('operation', operation);
    formData.append('matrix_source', dependenciesSource);
    // Append locks
    formData.append('locks', JSON.stringify(lockedDependencies));

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
        case 'move':
            formData.append('activity', document.getElementById('activity').value);
            
            const moveDependencyItems = document.querySelectorAll('.dependency-item');
            formData.append('dependency_count', moveDependencyItems.length);
            
            moveDependencyItems.forEach((item, index) => {
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
        case 'parallelize':
            formData.append('parallel_activities', document.getElementById('parallel_activities').value.split(',').map(s => s.trim()));
            break;
        case 'condition_update':
            formData.append('condition_activity', document.getElementById('condition_activity').value);
            formData.append('depending_activity', document.getElementById('depending_activity').value);
            break;
    }

    const originalDependenciesDisplay = document.getElementById('original-dependencies-display');
    const modifiedDependenciesDisplay = document.getElementById('modified-dependencies-display');
    
    document.getElementById('export-button').style.display = 'none';
    
    originalDependenciesDisplay.innerHTML = '<div class="alert alert-info"><span class="loading"></span> Performing operation...</div>';
    modifiedDependenciesDisplay.innerHTML = '<div class="alert alert-info"><span class="loading"></span> Performing operation...</div>';

    fetch('/api/change', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            modifiedDependenciesData = data.modified;
            
            displayDependencies(data.original, 'original-dependencies-display');
            displayDependencies(data.modified, 'modified-dependencies-display');
            console.log('Diff Info:', data.diff_info);
            
            const modifiedOption = document.querySelector('#dependencies-source-select option[value="modified"]');
            modifiedOption.disabled = false;
            modifiedOption.textContent = 'Modified Dependencies (Available)';
            
            // Update the source dependencies display if "modified" is currently selected
            const dependenciesSource = document.getElementById('dependencies-source-select').value;
            if (dependenciesSource === 'modified') {
                updateSourceDependenciesDisplay('modified');
            }
            
            document.getElementById('export-button').style.display = 'inline-block';
        } else {
            originalDependenciesDisplay.innerHTML = `<div class="alert alert-danger">Error: ${data.error}</div>`;
            modifiedDependenciesDisplay.innerHTML = `<div class="alert alert-danger">Error: ${data.error}</div>`;
            document.getElementById('export-button').style.display = 'none';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        originalDependenciesDisplay.innerHTML = '<div class="alert alert-danger">An unexpected error occurred.</div>';
        modifiedDependenciesDisplay.innerHTML = '<div class="alert alert-danger">An unexpected error occurred.</div>';
        // Hide export button on error
        document.getElementById('export-button').style.display = 'none';
    });
}

function exportModifiedDependencies() {
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
            alert('An error occurred while exporting the dependencies.');
        });
}

function updateDependenciesSourceTitle() {
    const dependenciesSource = document.getElementById('dependencies-source-select').value;
    const titleElement = document.getElementById('source-dependencies-title');
    const modifiedOption = document.querySelector('#dependencies-source-select option[value="modified"]');
    
    if (dependenciesSource === 'modified') {
        titleElement.textContent = 'Modified Dependencies (Source)';
        if (modifiedOption.disabled) {
            // If modified option is disabled, reset to original
            document.getElementById('dependencies-source-select').value = 'original';
            titleElement.textContent = 'Initial Dependencies (Source)';
            showDependenciesSourceStatus('original');
            updateSourceDependenciesDisplay('original');
        } else {
            showDependenciesSourceStatus('modified');
            updateSourceDependenciesDisplay('modified');
        }
    } else {
        titleElement.textContent = 'Initial Dependencies (Source)';
        showDependenciesSourceStatus('original');
        updateSourceDependenciesDisplay('original');
    }
}

function updateSourceDependenciesDisplay(dependenciesSource) {
    const sourceDisplay = document.getElementById('original-dependencies-display');
    
    if (dependenciesSource === 'modified' && modifiedDependenciesData) {
        displayDependencies(modifiedDependenciesData, 'original-dependencies-display');
    } else if (dependenciesSource === 'original' && originalDependenciesData) {
        displayDependencies(originalDependenciesData, 'original-dependencies-display');
    } else {
        sourceDisplay.innerHTML = '<div class="alert alert-info">Analyze dependencies first to perform operations on them.</div>';
    }
}

function showDependenciesSourceStatus(dependenciesSource) {
    const statusMessages = {
        'original': 'Using Initial Dependencies as source for operation',
        'modified': 'Using Modified Dependencies as source for operation'
    };
    
    let statusElement = document.getElementById('dependencies-source-status');
    if (!statusElement) {
        statusElement = document.createElement('div');
        statusElement.id = 'dependencies-source-status';
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
    
    statusElement.textContent = statusMessages[dependenciesSource] || '';
    statusElement.style.display = dependenciesSource ? 'block' : 'none';
}

function updateSourceDependenciesDisplayAlt(dependenciesSource) {
    const originalDependenciesDisplay = document.getElementById('original-dependencies-display');
    const modifiedDependenciesDisplay = document.getElementById('modified-dependencies-display');
    
    if (dependenciesSource === 'original' && originalDependenciesData) {
        displayDependencies(originalDependenciesData, 'original-dependencies-display');
    } else if (dependenciesSource === 'modified' && modifiedDependenciesData) {
        displayDependencies(modifiedDependenciesData, 'modified-dependencies-display');
    }
}

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('change-operation-select').addEventListener('change', updateOperationInputs);
    document.getElementById('dependencies-source-select').addEventListener('change', () => {
        updateDependenciesSourceTitle();
        showDependenciesSourceStatus(document.getElementById('dependencies-source-select').value);
    });
    
    // Initialize the "Modified Dependencies" option as disabled
    const modifiedOption = document.querySelector('#dependencies-source-select option[value="modified"]');
    modifiedOption.disabled = true;
    updateDependenciesSourceTitle();
    
    console.log('Business Process Redesign Tool initialized');
});