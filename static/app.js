// Global variables to store dependency data
let originalDependenciesData = null;
let modifiedDependenciesData = null;

let lockedDependencies = [];

function processInput() {
    // Hide any previous success message
    const successMessageContainer = document.getElementById('analysis-success-message');
    successMessageContainer.style.display = 'none';
    
    const tracesInput = document.getElementById('traces-input').value;
    const yamlFile = document.getElementById('yaml-file').files[0];

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
        alert('Please provide traces or upload a YAML file.');
        return;
    }

    fetch('/api/process', fetchOptions)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                fetchAndDisplayDependencies();
            } else {
                alert(`Error: ${data.error}`);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An unexpected error occurred.');
        });
}

function showAnalysisSuccessMessage(activityCount) {
    const successMessageContainer = document.getElementById('analysis-success-message');
    
    successMessageContainer.innerHTML = `
        <div class="alert alert-success">
            <strong>✓ Analysis Complete!</strong> Successfully analyzed dependencies for ${activityCount} activities. 
            You can now proceed with process redesign operations below.
        </div>
    `;
    
    successMessageContainer.style.display = 'block';
    
    // Auto-hide the message after 5 seconds
    setTimeout(() => {
        successMessageContainer.style.display = 'none';
    }, 5000);
}

function fetchAndDisplayDependencies() {
    fetch('/api/matrix')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                originalDependenciesData = data;
                modifiedDependenciesData = null; // Clear any previous modified dependencies
                
                document.getElementById('modified-dependencies-display').innerHTML = '<div class="alert alert-info">The result of the operation will be displayed here.</div>';
                
                // Reset dependencies source selection to "original" and disable "modified" option
                const dependenciesSourceSelect = document.getElementById('dependencies-source-select');
                dependenciesSourceSelect.value = 'original';
                const modifiedOption = document.querySelector('#dependencies-source-select option[value="modified"]');
                modifiedOption.disabled = true;
                modifiedOption.textContent = 'Modified Dependencies';
                populateLockSelections(data.activities);
                
                // Show success message
                showAnalysisSuccessMessage(data.activities.length);
            } else {
                alert(`Error: ${data.error}`);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to analyze dependencies.');
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

function displayDependenciesComparison(originalData, modifiedData, elementId) {
    const dependenciesDisplay = document.getElementById(elementId);
    
    let comparisonHtml = '<div class="dependencies-comparison">';
    comparisonHtml += '<h4>Dependency Changes Overview</h4>';
    comparisonHtml += '<div class="comparison-explanation">See what changed after the operation was performed:</div>';
    
    // Add detailed changes section (no Before/After sections)
    comparisonHtml += '<div class="detailed-changes">';
    comparisonHtml += '<h5>What Changed</h5>';

    const changes = compareDepencencies(originalData, modifiedData);
    // Show added activities and added cells explicitly if present in diff_info
    const diffInfo = modifiedData.diff_info || {};
    let hasChange = changes.length > 0;

    // Show added activities
    if (diffInfo.added_activities && diffInfo.added_activities.length > 0) {
        hasChange = true;
        diffInfo.added_activities.forEach(activity => {
            comparisonHtml += `<div class="change-item added-activity">Added Activity: <strong>${activity}</strong></div>`;
        });
    }
    // Show added cells (dependencies)
    if (diffInfo.added_cells && diffInfo.added_cells.length > 0) {
        hasChange = true;
        diffInfo.added_cells.forEach(cell => {
            const [from, to] = cell;
            comparisonHtml += `<div class="change-item added">New Dependency: <strong>${from} → ${to}</strong></div>`;
        });
    }

    // Show removed activities
    if (diffInfo.removed_activities && diffInfo.removed_activities.length > 0) {
        hasChange = true;
        diffInfo.removed_activities.forEach(activity => {
            comparisonHtml += `<div class="change-item removed-activity">Removed Activity: <strong>${activity}</strong></div>`;
        });
    }
    // Show removed cells (dependencies)
    if (diffInfo.removed_cells && diffInfo.removed_cells.length > 0) {
        hasChange = true;
        diffInfo.removed_cells.forEach(cell => {
            const [from, to] = cell;
            comparisonHtml += `<div class="change-item removed">Removed Dependency: <strong>${from} → ${to}</strong></div>`;
        });
    }
    // Show modified cells (dependencies)
    if (diffInfo.modified_cells && diffInfo.modified_cells.length > 0) {
        hasChange = true;
        diffInfo.modified_cells.forEach(cell => {
            const [from, to] = cell;
            comparisonHtml += `<div class="change-item modified">Modified Dependency: <strong>${from} → ${to}</strong></div>`;
        });
    }

    // Show other changes from compareDepencencies
    if (changes.length > 0) {
        changes.forEach(change => {
            comparisonHtml += `<div class="change-item ${change.type}">${change.details}</div>`;
        });
    }
    if (!hasChange) {
        comparisonHtml += '<div class="no-changes">No dependency changes detected.</div>';
    }
    comparisonHtml += '</div>'; // end detailed-changes
    
    // Add visual dependency graph section
    comparisonHtml += '<div class="dependency-graph-section">';
    comparisonHtml += '<h5>Visual Dependency Changes</h5>';
    comparisonHtml += '<div class="dependency-graph-container">';
    comparisonHtml += '<div id="dependency-graph"></div>';
    comparisonHtml += '</div>';
    comparisonHtml += '</div>'; // end dependency-graph-section
    comparisonHtml += '</div>'; // end dependencies-comparison
    
    dependenciesDisplay.innerHTML = comparisonHtml;
    
    // Create the visual dependency graph after DOM is updated
    if (changes.length > 0) {
        createDependencyGraph(originalData, modifiedData, changes);
    }
}

function getDependencyPairs(data) {
    const dependencies = [];
    const activities = data.activities;
    const matrix = data.matrix;
    
    activities.forEach(fromActivity => {
        activities.forEach(toActivity => {
            if (fromActivity !== toActivity && matrix[fromActivity] && matrix[fromActivity][toActivity]) {
                const cellContent = matrix[fromActivity][toActivity];
                if (cellContent && cellContent !== '' && cellContent !== '-,-') {
                    const explanation = parseDependencyExplanationCompact(cellContent, fromActivity, toActivity);
                    const detailed = parseDependencyExplanation(cellContent, fromActivity, toActivity);
                    dependencies.push({
                        from: fromActivity,
                        to: toActivity,
                        content: cellContent,
                        explanation: explanation,
                        detailed: detailed
                    });
                }
            }
        });
    });
    
    return dependencies;
}

function parseDependencyExplanationCompact(cellContent, fromActivity, toActivity) {
    const parts = cellContent.split(',');
    const temporalPart = parts[0] || '-';
    const existentialPart = parts[1] || '-';
    
    let explanations = [];
    
    // Temporal dependency explanation (compact)
    if (temporalPart !== '-') {
        if (temporalPart.includes('≺')) {
            if (temporalPart.includes('d')) {
                explanations.push(`${fromActivity} directly before ${toActivity}`);
            } else {
                explanations.push(`${fromActivity} before ${toActivity}`);
            }
        } else if (temporalPart.includes('≻')) {
            if (temporalPart.includes('d')) {
                explanations.push(`${toActivity} directly before ${fromActivity}`);
            } else {
                explanations.push(`${toActivity} before ${fromActivity}`);
            }
        }
    }
    
    // Existential dependency explanation (compact)
    if (existentialPart !== '-') {
        if (existentialPart === '=>') {
            explanations.push(`if ${fromActivity} then ${toActivity}`);
        } else if (existentialPart === '<=') {
            explanations.push(`if ${toActivity} then ${fromActivity}`);
        } else if (existentialPart === '⇔') {
            explanations.push(`${fromActivity} and ${toActivity} together`);
        } else if (existentialPart === '⇎') {
            explanations.push(`${fromActivity} or ${toActivity}, not both`);
        } else if (existentialPart === '∧') {
            explanations.push(`${fromActivity} and ${toActivity} must occur`);
        } else if (existentialPart === '⊼') {
            explanations.push(`${fromActivity} and ${toActivity} cannot both occur`);
        } else if (existentialPart === '∨') {
            explanations.push(`${fromActivity} or ${toActivity} must occur`);
        }
    }
    
    return explanations.length > 0 ? explanations.join(', ') : 'no constraints';
}

function compareDepencencies(originalData, modifiedData) {
    const changes = [];
    
    const originalDeps = getDependencyPairs(originalData);
    const modifiedDeps = getDependencyPairs(modifiedData);
    
    // Helper function to check if two dependencies are of compatible types for modification
    function areCompatibleTypes(type1, type2) {
        const temporalTypes = ['Direct Forward Temporal', 'Eventual Forward Temporal', 'Direct Backward Temporal', 'Eventual Backward Temporal'];
        const existentialTypes = ['Forward Implication', 'Backward Implication', 'Equivalence', 'Negated Equivalence', 'AND', 'NAND', 'OR'];
        
        // Check if both are temporal types
        const type1IsTemporal = temporalTypes.some(temp => type1.includes(temp));
        const type2IsTemporal = temporalTypes.some(temp => type2.includes(temp));
        
        // Check if both are existential types  
        const type1IsExistential = existentialTypes.some(exist => type1.includes(exist));
        const type2IsExistential = existentialTypes.some(exist => type2.includes(exist));
        
        // They are compatible if they are both temporal or both existential
        return (type1IsTemporal && type2IsTemporal) || (type1IsExistential && type2IsExistential);
    }
    
    // Helper function to check if a dependency is truly removed (not just became independence)
    function isDependencyTrulyRemoved(originalDep, modifiedData) {
        const modifiedMatrix = modifiedData.matrix;
        const modifiedCellContent = modifiedMatrix[originalDep.from] && modifiedMatrix[originalDep.from][originalDep.to];
        
        // If the cell doesn't exist in modified matrix or is completely empty, it's truly removed
        // If it's '-,-' (independence), it's not removed, just became independent
        return !modifiedCellContent || modifiedCellContent === '';
    }
    
    // Find removed dependencies (only when truly removed, not when becoming independent)
    originalDeps.forEach(originalDep => {
        if (isDependencyTrulyRemoved(originalDep, modifiedData)) {
            const dependencyType = identifyDependencyType(originalDep.content);
            changes.push({
                type: 'removed',
                description: `Removed: ${originalDep.from} → ${originalDep.to}`,
                tooltip: `This dependency was completely removed.\n\nType: ${dependencyType}\nDescription: ${originalDep.explanation}`,
                from: originalDep.from,
                to: originalDep.to,
                details: `Removed: ${originalDep.from} → ${originalDep.to} (was: ${dependencyType} - ${originalDep.explanation})`
            });
        }
    });
    
    // Find added dependencies
    modifiedDeps.forEach(modifiedDep => {
        const originalMatrix = originalData.matrix;
        const originalCellContent = originalMatrix[modifiedDep.from] && originalMatrix[modifiedDep.from][modifiedDep.to];
        
        // Only consider it added if it didn't exist before or was empty (not if it was independence)
        if (!originalCellContent || originalCellContent === '') {
            const dependencyType = identifyDependencyType(modifiedDep.content);
            changes.push({
                type: 'added',
                description: `Added: ${modifiedDep.from} → ${modifiedDep.to}`,
                tooltip: `This dependency was added.\n\nType: ${dependencyType}\nDescription: ${modifiedDep.explanation}`,
                from: modifiedDep.from,
                to: modifiedDep.to,
                details: `Added: ${modifiedDep.from} → ${modifiedDep.to} (now: ${dependencyType} - ${modifiedDep.explanation})`
            });
        }
    });
    
    // Find modified dependencies (only between compatible types)
    originalDeps.forEach(originalDep => {
        const modifiedDep = modifiedDeps.find(dep => 
            dep.from === originalDep.from && dep.to === originalDep.to
        );
        if (modifiedDep && modifiedDep.content !== originalDep.content) {
            const originalType = identifyDependencyType(originalDep.content);
            const modifiedType = identifyDependencyType(modifiedDep.content);
            
            // Only show changes between compatible types
            if (areCompatibleTypes(originalType, modifiedType)) {
                changes.push({
                    type: 'modified',
                    description: `Modified: ${originalDep.from} → ${originalDep.to}`,
                    tooltip: `This dependency was changed:\n\nWAS: ${originalType}\nNOW: ${modifiedType}\n\nBefore: ${originalDep.explanation}\nAfter: ${modifiedDep.explanation}`,
                    from: originalDep.from,
                    to: originalDep.to,
                    details: `Modified: ${originalDep.from} → ${originalDep.to} (was: ${originalType} - ${originalDep.explanation} | now: ${modifiedType} - ${modifiedDep.explanation})`
                });
            }
        }
    });
    
    // Find removed activities
    const originalActivities = originalData.activities;
    const modifiedActivities = modifiedData.activities;
    
    originalActivities.forEach(activity => {
        if (!modifiedActivities.includes(activity)) {
            changes.push({
                type: 'removed-activity',
                description: `Activity "${activity}" removed`,
                tooltip: `Activity "${activity}" was removed from the process`,
                activity: activity,
                details: `Removed: Activity "${activity}" was removed from the process`
            });
        }
    });
    
    // Find added activities
    modifiedActivities.forEach(activity => {
        if (!originalActivities.includes(activity)) {
            changes.push({
                type: 'added-activity', 
                description: `Activity "${activity}" added`,
                tooltip: `Activity "${activity}" was added to the process`,
                activity: activity,
                details: `Added: Activity "${activity}" was added to the process`
            });
        }
    });
    
    return changes;
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

    const modifiedDependenciesDisplay = document.getElementById('modified-dependencies-display');
    
    document.getElementById('export-button').style.display = 'none';
    
    modifiedDependenciesDisplay.innerHTML = '<div class="alert alert-info"><span class="loading"></span> Performing operation...</div>';

    fetch('/api/change', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            modifiedDependenciesData = data.modified;
            
            displayDependenciesComparison(data.original, data.modified, 'modified-dependencies-display');
            console.log('Diff Info:', data.diff_info);
            
            const modifiedOption = document.querySelector('#dependencies-source-select option[value="modified"]');
            modifiedOption.disabled = false;
            modifiedOption.textContent = 'Modified Dependencies (Available)';
            
            document.getElementById('export-button').style.display = 'inline-block';
        } else {
            modifiedDependenciesDisplay.innerHTML = `<div class="alert alert-danger">Error: ${data.error}</div>`;
            document.getElementById('export-button').style.display = 'none';
        }
    })
    .catch(error => {
        console.error('Error:', error);
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


function createDependencyGraph(originalData, modifiedData, changes) {
    const graphContainer = document.getElementById('dependency-graph');
    if (!graphContainer) return;
    
    // Get all unique activities from both datasets
    const allActivities = [...new Set([...originalData.activities, ...modifiedData.activities])];
    
    // Calculate graph dimensions
    const containerWidth = graphContainer.offsetWidth || 800;
    const containerHeight = Math.max(400, allActivities.length * 60);
    const nodeRadius = 25;
    const padding = 50;
    
    // Clear previous content
    graphContainer.innerHTML = '';
    
    // Create SVG
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('width', containerWidth);
    svg.setAttribute('height', containerHeight);
    svg.setAttribute('viewBox', `0 0 ${containerWidth} ${containerHeight}`);
    svg.style.background = 'var(--bg-primary)';
    svg.style.borderRadius = '8px';
    svg.style.border = '1px solid var(--border-color)';
    
    // Calculate node positions in a circular layout
    const centerX = containerWidth / 2;
    const centerY = containerHeight / 2;
    const radius = Math.min(centerX, centerY) - padding - nodeRadius;
    
    const nodePositions = {};
    allActivities.forEach((activity, index) => {
        const angle = (2 * Math.PI * index) / allActivities.length;
        nodePositions[activity] = {
            x: centerX + radius * Math.cos(angle),
            y: centerY + radius * Math.sin(angle)
        };
    });
    
    // Create edges first (so they appear behind nodes)
    const edgeElements = [];
    
    // Get all dependencies from both original and modified data
    const originalDeps = getDependencyPairs(originalData);
    const modifiedDeps = getDependencyPairs(modifiedData);
    
    // Create a map to track edge types
    const edgeMap = new Map();
    
    // Process original dependencies
    originalDeps.forEach(dep => {
        const key = `${dep.from}-${dep.to}`;
        edgeMap.set(key, {
            from: dep.from,
            to: dep.to,
            originalExplanation: dep.explanation,
            originalDetailed: dep.detailed || dep.explanation,
            originalContent: dep.content,
            type: 'existing'
        });
    });
    
    // Process modified dependencies
    modifiedDeps.forEach(dep => {
        const key = `${dep.from}-${dep.to}`;
        if (edgeMap.has(key)) {
            const existing = edgeMap.get(key);
            existing.modifiedExplanation = dep.explanation;
            existing.modifiedDetailed = dep.detailed || dep.explanation;
            existing.modifiedContent = dep.content;
            existing.type = existing.originalExplanation === dep.explanation ? 'existing' : 'modified';
        } else {
            edgeMap.set(key, {
                from: dep.from,
                to: dep.to,
                modifiedExplanation: dep.explanation,
                modifiedDetailed: dep.detailed || dep.explanation,
                modifiedContent: dep.content,
                type: 'added'
            });
        }
    });
    
    // Mark removed dependencies
    originalDeps.forEach(dep => {
        const key = `${dep.from}-${dep.to}`;
        const edge = edgeMap.get(key);
        if (edge && !edge.modifiedExplanation) {
            edge.type = 'removed';
        }
    });
    
    // Create edges
    edgeMap.forEach((edge, key) => {
        const fromPos = nodePositions[edge.from];
        const toPos = nodePositions[edge.to];
        
        if (!fromPos || !toPos) return;
        
        // Calculate edge positions (from edge of circles, not centers)
        const dx = toPos.x - fromPos.x;
        const dy = toPos.y - fromPos.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        const unitX = dx / distance;
        const unitY = dy / distance;
        
        const startX = fromPos.x + unitX * nodeRadius;
        const startY = fromPos.y + unitY * nodeRadius;
        const endX = toPos.x - unitX * nodeRadius;
        const endY = toPos.y - unitY * nodeRadius;
        
        // Create line element (no arrowheads)
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', startX);
        line.setAttribute('y1', startY);
        line.setAttribute('x2', endX);
        line.setAttribute('y2', endY);
        line.setAttribute('stroke-width', '3');
        line.classList.add('dependency-edge', `edge-${edge.type}`);
        
        // Set color based on change type
        let strokeColor;
        switch (edge.type) {
            case 'added':
                strokeColor = '#27AE60'; // Brighter green for better contrast with yellow
                break;
            case 'removed':
                strokeColor = '#FF6B35'; // Orange
                break;
            case 'modified':
                strokeColor = '#FFDC00'; // TUM Yellow
                break;
            default:
                strokeColor = '#6A757E'; // Muted grey for existing
        }
        line.setAttribute('stroke', strokeColor);
        
        // Add verbose hover tooltip
        let tooltipText = '';
        switch (edge.type) {
            case 'added':
                const addedType = identifyDependencyType(edge.modifiedContent);
                tooltipText = `DEPENDENCY ADDED\n\nNew dependency: ${edge.from} ↔ ${edge.to}\nDependency Type: ${addedType}\n\nDetailed explanation:\n${createVerboseExplanation(edge.modifiedDetailed || edge.modifiedExplanation, edge.from, edge.to)}`;
                break;
            case 'removed':
                const removedType = identifyDependencyType(edge.originalContent);
                tooltipText = `DEPENDENCY REMOVED\n\nRemoved dependency: ${edge.from} ↔ ${edge.to}\nDependency Type: ${removedType}\n\nWhat was removed:\n${createVerboseExplanation(edge.originalDetailed || edge.originalExplanation, edge.from, edge.to)}`;
                break;
            case 'modified':
                const originalType = identifyDependencyType(edge.originalContent);
                const modifiedType = identifyDependencyType(edge.modifiedContent);
                tooltipText = `DEPENDENCY MODIFIED\n\nChanged dependency: ${edge.from} ↔ ${edge.to}\n\nWAS: ${originalType}\nNOW: ${modifiedType}\n\nBefore:\n${createVerboseExplanation(edge.originalDetailed || edge.originalExplanation, edge.from, edge.to)}\n\nAfter:\n${createVerboseExplanation(edge.modifiedDetailed || edge.modifiedExplanation, edge.from, edge.to)}`;
                break;
            default:
                const existingType = identifyDependencyType(edge.originalContent || edge.modifiedContent);
                tooltipText = `UNCHANGED DEPENDENCY\n\nExisting dependency: ${edge.from} ↔ ${edge.to}\nDependency Type: ${existingType}\n\nExplanation:\n${createVerboseExplanation(edge.originalDetailed || edge.originalExplanation || edge.modifiedDetailed || edge.modifiedExplanation, edge.from, edge.to)}`;
        }
        
        line.innerHTML = `<title>${tooltipText}</title>`;
        
        svg.appendChild(line);
        edgeElements.push(line);
    });
    
    // Create nodes (on top of edges)
    allActivities.forEach(activity => {
        const pos = nodePositions[activity];
        const isRemoved = !modifiedData.activities.includes(activity);
        const isAdded = !originalData.activities.includes(activity);
        
        // Create circle
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('cx', pos.x);
        circle.setAttribute('cy', pos.y);
        circle.setAttribute('r', nodeRadius);
        circle.classList.add('activity-node');
        
        // Set colors based on activity status
        if (isAdded) {
            circle.setAttribute('fill', '#27AE60');
            circle.setAttribute('stroke', '#1E8449');
        } else if (isRemoved) {
            circle.setAttribute('fill', '#FF6B35');
            circle.setAttribute('stroke', '#CC5429');
        } else {
            circle.setAttribute('fill', '#0065BD');
            circle.setAttribute('stroke', '#004A8C');
        }
        circle.setAttribute('stroke-width', '2');
        
        // Add activity label
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', pos.x);
        text.setAttribute('y', pos.y + 5);
        text.setAttribute('text-anchor', 'middle');
        text.setAttribute('fill', '#FFFFFF');
        text.setAttribute('font-family', 'Arial, sans-serif');
        text.setAttribute('font-weight', 'bold');
        text.setAttribute('font-size', '12');
        text.textContent = activity;
        text.classList.add('activity-label');
        
        // Add tooltip for activity status
        let activityTooltip = `ACTIVITY: ${activity}`;
        if (isAdded) activityTooltip += '\n\nSTATUS: This activity was added to the process';
        else if (isRemoved) activityTooltip += '\n\nSTATUS: This activity was removed from the process';
        else activityTooltip += '\n\nSTATUS: This activity remains unchanged in the process';
        
        circle.innerHTML = `<title>${activityTooltip}</title>`;
        
        svg.appendChild(circle);
        svg.appendChild(text);
    });
    
    // Add legend
    const legend = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    legend.setAttribute('transform', 'translate(10, 10)');
    
    const legendItems = [
        { color: '#27AE60', label: 'Added', type: 'edge' },
        { color: '#FF6B35', label: 'Removed', type: 'edge' },
        { color: '#FFDC00', label: 'Modified', type: 'edge' },
        { color: '#6A757E', label: 'Unchanged', type: 'edge' }
    ];
    
    legendItems.forEach((item, index) => {
        const y = index * 20;
        
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', 0);
        line.setAttribute('y1', y + 10);
        line.setAttribute('x2', 20);
        line.setAttribute('y2', y + 10);
        line.setAttribute('stroke', item.color);
        line.setAttribute('stroke-width', '3');
        legend.appendChild(line);
        
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', 25);
        text.setAttribute('y', y + 14);
        text.setAttribute('fill', '#FFFFFF');
        text.setAttribute('font-family', 'Arial, sans-serif');
        text.setAttribute('font-size', '12');
        text.textContent = item.label;
        legend.appendChild(text);
    });
    
    svg.appendChild(legend);
    graphContainer.appendChild(svg);
}

// Create verbose explanation for tooltips
function createVerboseExplanation(explanation, fromActivity, toActivity) {
    // If explanation already contains HTML or detailed text, strip HTML and use it
    if (explanation && (explanation.includes('must happen') || explanation.includes('Timing:') || explanation.includes('Occurrence:'))) {
        // Strip HTML tags and extract the meaningful text
        return explanation.replace(/<[^>]*>/g, '').replace(/&[^;]+;/g, ' ').trim();
    }
    
    // If it's a compact explanation, try to expand it based on patterns
    if (explanation && explanation.includes('directly before')) {
        return `${fromActivity} must happen immediately before ${toActivity} with no other activities in between.\n\nThis is a DIRECT TEMPORAL DEPENDENCY that enforces strict ordering.`;
    } else if (explanation && explanation.includes(' before ')) {
        return `${fromActivity} must happen before ${toActivity}, but other activities can happen in between.\n\nThis is an EVENTUAL TEMPORAL DEPENDENCY that allows flexibility in execution.`;
    } else if (explanation && explanation.includes('if') && explanation.includes('then')) {
        return `If ${fromActivity} occurs in a process instance, then ${toActivity} must also occur in that same instance.\n\nThis is an IMPLICATION DEPENDENCY that links the existence of these activities.`;
    } else if (explanation && explanation.includes('both happen or both not happen')) {
        return `${fromActivity} and ${toActivity} must always occur together - either both happen or neither happens in any process instance.\n\nThis is an EQUIVALENCE DEPENDENCY that ensures mutual occurrence.`;
    } else if (explanation && explanation.includes('cannot both occur')) {
        return `${fromActivity} and ${toActivity} cannot both occur in the same process instance.\n\nThis is a NAND DEPENDENCY that prevents simultaneous execution.`;
    } else if (explanation && explanation.includes('and') && explanation.includes('must occur')) {
        return `Both ${fromActivity} and ${toActivity} must occur together in every process instance.\n\nThis is an AND DEPENDENCY that requires both activities.`;
    } else if (explanation && explanation.includes('or') && explanation.includes('must occur')) {
        return `At least one of ${fromActivity} or ${toActivity} must occur in every process instance.\n\nThis is an OR DEPENDENCY that requires at least one activity.`;
    } else if (explanation && explanation.includes('not both')) {
        return `Either ${fromActivity} or ${toActivity} can happen, but not both.\n\nThis is a MUTUAL EXCLUSION DEPENDENCY that allows only one activity.`;
    }
    
    // Fallback for any other explanation
    return explanation || 'No specific dependency constraint between these activities - they can occur independently.';
}

// Function to identify formal dependency type from cell content
function identifyDependencyType(cellContent) {
    if (!cellContent || cellContent === '-,-') return 'No constraint';
    
    const parts = cellContent.split(',');
    const temporalPart = parts[0] || '-';
    const existentialPart = parts[1] || '-';
    
    let types = [];
    
    // Identify temporal dependency type
    if (temporalPart !== '-') {
        if (temporalPart.includes('≺d')) {
            types.push('Direct Forward Temporal');
        } else if (temporalPart.includes('≺')) {
            types.push('Eventual Forward Temporal');
        } else if (temporalPart.includes('≻d')) {
            types.push('Direct Backward Temporal');
        } else if (temporalPart.includes('≻')) {
            types.push('Eventual Backward Temporal');
        }
    }
    
    // Identify existential dependency type
    if (existentialPart !== '-') {
        if (existentialPart === '=>') {
            types.push('Forward Implication');
        } else if (existentialPart === '<=') {
            types.push('Backward Implication');
        } else if (existentialPart === '⇔') {
            types.push('Equivalence');
        } else if (existentialPart === '⇎') {
            types.push('Negated Equivalence');
        } else if (existentialPart === '∧') {
            types.push('AND');
        } else if (existentialPart === '⊼') {
            types.push('NAND');
        } else if (existentialPart === '∨') {
            types.push('OR');
        }
    }
    
    return types.length > 0 ? types.join(' + ') : 'No constraint';
}

// Initialize page


// --- BPMN Operations UI ---
function fetchBpmnOperations() {
    fetch('/api/bpmn_demo')
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                showBpmnOperations(data.operations);
            }
        });
}

function showBpmnOperations(operations) {
    const listDiv = document.getElementById('bpmn-operations-list');
    listDiv.innerHTML = '';
    operations.forEach(op => {
        const btn = document.createElement('button');
        btn.className = 'btn btn-outline-primary';
        btn.style.margin = '0.5rem';
        btn.textContent = `${op.id}. ${op.title}`;
        btn.onclick = () => applyBpmnOperation(op);
        listDiv.appendChild(btn);
    });
}

function applyBpmnOperation(op) {
    fetch('/api/matrix')
        .then(res => res.json())
        .then(data => {
            const formData = new FormData();
            formData.append('operation', op.formal_input.operation);
            formData.append('matrix_source', 'original');
            formData.append('locks', '[]'); // Use hardcoded locks in backend

            // Fill in operation-specific fields
            if (op.formal_input.operation === 'insert') {
                formData.append('activity', op.formal_input.activity);
                const deps = op.formal_input.dependencies;
                formData.append('dependency_count', deps.length);
                deps.forEach((dep, i) => {
                    formData.append(`from_activity_${i}`, dep.from);
                    formData.append(`to_activity_${i}`, dep.to);
                    formData.append(`temporal_dep_${i}`, dep.temporal);
                    formData.append(`temporal_direction_${i}`, 'FORWARD');
                    formData.append(`existential_dep_${i}`, dep.existential);
                    if (dep.existential_direction) {
                        formData.append(`existential_direction_${i}`, dep.existential_direction);
                    } else {
                        formData.append(`existential_direction_${i}`, 'BOTH');
                    }
                });
            } else if (op.formal_input.operation === 'delete') {
                formData.append('activity', op.formal_input.activity);
            } else if (op.formal_input.operation === 'modify') {
                formData.append('from_activity', op.formal_input.from_activity);
                formData.append('to_activity', op.formal_input.to_activity);
                if (op.formal_input.temporal_dep) {
                    formData.append('temporal_dep', op.formal_input.temporal_dep);
                    formData.append('temporal_direction', 'FORWARD');
                }
                if (op.formal_input.existential_dep) {
                    formData.append('existential_dep', op.formal_input.existential_dep);
                    formData.append('existential_direction', 'BOTH');
                }
            } else if (op.formal_input.operation === 'move') {
                formData.append('activity', op.formal_input.activity);
                const deps = op.formal_input.dependencies;
                formData.append('dependency_count', deps.length);
                deps.forEach((dep, i) => {
                    formData.append(`from_activity_${i}`, dep.from);
                    formData.append(`to_activity_${i}`, dep.to);
                    formData.append(`temporal_dep_${i}`, dep.temporal);
                    formData.append(`temporal_direction_${i}`, 'FORWARD');
                    formData.append(`existential_dep_${i}`, dep.existential);
                    formData.append(`existential_direction_${i}`, 'BOTH');
                });
            } else if (op.formal_input.operation === 'skip') {
                formData.append('activity_to_skip', op.formal_input.activity);
            }

            // Show operation details above result
            const detailsDiv = document.getElementById('modified-dependencies-display');
            detailsDiv.innerHTML = `<div class='alert alert-info'><strong>${op.id}. ${op.title}</strong><br>${op.description}<br><pre>${JSON.stringify(op.formal_input, null, 2)}</pre><span class='loading'></span> Applying operation...</div>`;

            fetch('/api/change', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    displayDependenciesComparison(data.original, data.modified, 'modified-dependencies-display');
                    document.getElementById('export-button').style.display = 'inline-block';
                } else {
                    detailsDiv.innerHTML = `<div class='alert alert-danger'>Error: ${data.error}</div>`;
                    document.getElementById('export-button').style.display = 'none';
                }
            })
            .catch(error => {
                detailsDiv.innerHTML = `<div class='alert alert-danger'>An unexpected error occurred.</div>`;
                document.getElementById('export-button').style.display = 'none';
            });
        });
}

document.addEventListener('DOMContentLoaded', function() {
    fetchBpmnOperations();
    console.log('Business Process Redesign Tool initialized');
});