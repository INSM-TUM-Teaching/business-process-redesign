import sys
import os
import yaml
from werkzeug.utils import secure_filename
from adjacency_matrix import AdjacencyMatrix, parse_yaml_to_adjacency_matrix


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, jsonify
from traces_to_matrix import traces_to_adjacency_matrix
from dependencies import TemporalType, ExistentialType, Direction, TemporalDependency, ExistentialDependency
from change_operations.delete_operation import delete_activity
from change_operations.swap_operation import swap_activities
from change_operations.skip_operation import skip_activity
from change_operations.replace_operation import replace_activity
from change_operations.collapse_operation import collapse_operation
from change_operations.de_collapse_operation import decollapse_operation

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'temp_uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

current_matrix = None

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/api/process", methods=["POST"])
def process_input():
    """Process either traces or a YAML file to generate an adjacency matrix."""
    global current_matrix
    
    try:
        if 'file' in request.files and request.files['file'].filename != '':
            file = request.files['file']
            if file and (file.filename.endswith('.yaml') or file.filename.endswith('.yml')):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                current_matrix = parse_yaml_to_adjacency_matrix(filepath)
                
                os.remove(filepath) # Clean up the temporary file
            else:
                return jsonify({"success": False, "error": "Invalid file type. Please upload a YAML file."})

        else:
            data = request.get_json()
            traces = data.get('traces', [])
            if not traces:
                return jsonify({"success": False, "error": "No traces provided"})
            
            current_matrix = traces_to_adjacency_matrix(traces)

        return jsonify({"success": True, "message": "Matrix generated successfully."})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/matrix", methods=["GET"])
def get_matrix():
    """Return the current adjacency matrix."""
    if current_matrix is None:
        return jsonify({"success": False, "error": "Matrix not generated yet."})

    activities = current_matrix.activities
    matrix_display = {}

    for from_activity in activities:
        matrix_display[from_activity] = {}
        for to_activity in activities:
            if from_activity == to_activity:
                matrix_display[from_activity][to_activity] = "X"
                continue

            dep_tuple = current_matrix.get_dependency(from_activity, to_activity)
            if dep_tuple:
                temporal_dep, existential_dep = dep_tuple
                
                is_temporal_independence = False
                temporal_str = "-"
                if temporal_dep:
                    if temporal_dep.type == TemporalType.INDEPENDENCE:
                        is_temporal_independence = True
                    else:
                        direction_symbol = "-"
                        if temporal_dep.direction == Direction.FORWARD:
                            direction_symbol = "≺"
                        elif temporal_dep.direction == Direction.BACKWARD:
                            direction_symbol = "≻"
                        
                        type_symbol = ""
                        if temporal_dep.type == TemporalType.DIRECT:
                            type_symbol = "d"
                        
                        temporal_str = f"{direction_symbol}{type_symbol}"

                is_existential_independence = False
                existential_str = "-"
                if existential_dep:
                    if existential_dep.type == ExistentialType.INDEPENDENCE:
                        is_existential_independence = True
                    elif existential_dep.type == ExistentialType.IMPLICATION:
                        if existential_dep.direction == Direction.FORWARD:
                            existential_str = "=>"
                        elif existential_dep.direction == Direction.BACKWARD:
                            existential_str = "<="
                    elif existential_dep.type == ExistentialType.EQUIVALENCE:
                        existential_str = "⇔"
                    elif existential_dep.type == ExistentialType.NEGATED_EQUIVALENCE:
                        existential_str = "⇎"
                    elif existential_dep.type == ExistentialType.NAND:
                        existential_str = "⊼"
                    elif existential_dep.type == ExistentialType.OR:
                        existential_str = "∨"

                if is_temporal_independence and is_existential_independence:
                    matrix_display[from_activity][to_activity] = "-,-"
                elif temporal_str != "-" or existential_str != "-":
                    matrix_display[from_activity][to_activity] = f"{temporal_str},{existential_str}"
                else:
                    matrix_display[from_activity][to_activity] = ""
            else:
                matrix_display[from_activity][to_activity] = ""

    return jsonify({
        "success": True,
        "activities": activities,
        "matrix": matrix_display
    })

@app.route("/api/change", methods=["POST"])
def change_matrix():
    """Perform a change operation on the current matrix."""
    global current_matrix
    if current_matrix is None:
        return jsonify({"success": False, "error": "Matrix not generated yet."})

    try:
        operation = request.form.get('operation')
        modified_matrix = None

        if operation == 'delete':
            activity = request.form.get('activity')
            modified_matrix = delete_activity(current_matrix, activity)
        elif operation == 'swap':
            activity1 = request.form.get('activity1')
            activity2 = request.form.get('activity2')
            modified_matrix = swap_activities(current_matrix, activity1, activity2)
        elif operation == 'skip':
            activity = request.form.get('activity_to_skip')
            modified_matrix = skip_activity(current_matrix, activity)
        elif operation == 'replace':
            old_activity = request.form.get('old_activity')
            new_activity = request.form.get('new_activity')
            modified_matrix = replace_activity(current_matrix, old_activity, new_activity)
        elif operation == 'collapse':
            collapsed_activity = request.form.get('collapsed_activity')
            collapse_activities = request.form.get('collapse_activities').split(',')
            modified_matrix = collapse_operation(current_matrix, collapsed_activity, collapse_activities)
        elif operation == 'de-collapse':
            collapsed_activity = request.form.get('collapsed_activity')
            
            if 'collapsed_matrix_file' not in request.files:
                return jsonify({"success": False, "error": "No collapsed matrix file provided."})
            
            file = request.files['collapsed_matrix_file']
            if file and (file.filename.endswith('.yaml') or file.filename.endswith('.yml')):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                collapsed_matrix = parse_yaml_to_adjacency_matrix(filepath)
                
                os.remove(filepath)
                modified_matrix = decollapse_operation(current_matrix, collapsed_activity, collapsed_matrix)
            else:
                return jsonify({"success": False, "error": "Invalid file type for collapsed matrix."})

        if modified_matrix:
            activities = modified_matrix.activities
            matrix_display = {}
            for from_activity in activities:
                matrix_display[from_activity] = {}
                for to_activity in activities:
                    if from_activity == to_activity:
                        matrix_display[from_activity][to_activity] = "X"
                        continue

                    dep_tuple = modified_matrix.get_dependency(from_activity, to_activity)
                    if dep_tuple:
                        temporal_dep, existential_dep = dep_tuple
                        
                        is_temporal_independence = False
                        temporal_str = "-"
                        if temporal_dep:
                            if temporal_dep.type == TemporalType.INDEPENDENCE:
                                is_temporal_independence = True
                            else:
                                direction_symbol = "-"
                                if temporal_dep.direction == Direction.FORWARD:
                                    direction_symbol = "≺"
                                elif temporal_dep.direction == Direction.BACKWARD:
                                    direction_symbol = "≻"
                                
                                type_symbol = ""
                                if temporal_dep.type == TemporalType.DIRECT:
                                    type_symbol = "d"
                                
                                temporal_str = f"{direction_symbol}{type_symbol}"

                        is_existential_independence = False
                        existential_str = "-"
                        if existential_dep:
                            if existential_dep.type == ExistentialType.INDEPENDENCE:
                                is_existential_independence = True
                            elif existential_dep.type == ExistentialType.IMPLICATION:
                                if existential_dep.direction == Direction.FORWARD:
                                    existential_str = "=>"
                                elif existential_dep.direction == Direction.BACKWARD:
                                    existential_str = "<="
                            elif existential_dep.type == ExistentialType.EQUIVALENCE:
                                existential_str = "⇔"
                            elif existential_dep.type == ExistentialType.NEGATED_EQUIVALENCE:
                                existential_str = "⇎"
                            elif existential_dep.type == ExistentialType.NAND:
                                existential_str = "⊼"
                            elif existential_dep.type == ExistentialType.OR:
                                existential_str = "∨"

                        if is_temporal_independence and is_existential_independence:
                            matrix_display[from_activity][to_activity] = "-,-"
                        elif temporal_str != "-" or existential_str != "-":
                            matrix_display[from_activity][to_activity] = f"{temporal_str},{existential_str}"
                        else:
                            matrix_display[from_activity][to_activity] = ""
                    else:
                        matrix_display[from_activity][to_activity] = ""
            
            return jsonify({
                "success": True,
                "activities": activities,
                "matrix": matrix_display
            })
        else:
            return jsonify({"success": False, "error": "Operation not supported or failed."})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
