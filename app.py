import sys
import os
import yaml
from adjacency_matrix import AdjacencyMatrix


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, jsonify
from traces_to_matrix import traces_to_adjacency_matrix
from dependencies import TemporalType, ExistentialType, Direction, TemporalDependency, ExistentialDependency

app = Flask(__name__)

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
            if file.filename.endswith('.yaml') or file.filename.endswith('.yml'):
                yaml_data = yaml.safe_load(file.stream)
                
                metadata = yaml_data.get('metadata', {})
                activities = metadata.get('activities', [])
                dependencies = yaml_data.get('dependencies', [])

                current_matrix = AdjacencyMatrix(activities=activities)

                for dep in dependencies:
                    from_activity = dep.get('from')
                    to_activity = dep.get('to')
                    
                    if not from_activity or not to_activity:
                        continue
                    
                    temporal_dep = None
                    if 'temporal' in dep:
                        temporal_data = dep['temporal']
                        dep_type_str = temporal_data.get('type', '').upper()
                        direction_str = temporal_data.get('direction', '').upper()
                        
                        try:
                            dep_type = TemporalType[dep_type_str] if dep_type_str else None
                            direction = Direction[direction_str] if direction_str else None

                            if dep_type and direction:
                                temporal_dep = TemporalDependency(dep_type, direction)
                        except KeyError:
                            pass # Ignore if type or direction is invalid

                    existential_dep = None
                    if 'existential' in dep:
                        existential_data = dep['existential']
                        dep_type_str = existential_data.get('type', '').upper()
                        direction_str = existential_data.get('direction', '').upper()
                        
                        try:
                            dep_type = ExistentialType[dep_type_str] if dep_type_str else None
                            direction = Direction[direction_str] if direction_str else None

                            if dep_type and direction:
                                existential_dep = ExistentialDependency(dep_type, direction)
                        except KeyError:
                            pass # Ignore if type or direction is invalid
                    
                    if temporal_dep or existential_dep:
                        current_matrix.add_dependency(from_activity, to_activity, temporal_dep, existential_dep)

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
                
                temporal_str = "-"
                if temporal_dep:
                    direction_symbol = ""
                    if temporal_dep.direction == Direction.FORWARD:
                        direction_symbol = "≺"
                    elif temporal_dep.direction == Direction.BACKWARD:
                        direction_symbol = "≻"
                    
                    type_symbol = ""
                    if temporal_dep.type == TemporalType.DIRECT:
                        type_symbol = "d"
                    
                    temporal_str = f"{direction_symbol}{type_symbol}"

                existential_str = "-"
                if existential_dep:
                    if existential_dep.type == ExistentialType.IMPLICATION:
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

                if temporal_str != "-" or existential_str != "-":
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

if __name__ == "__main__":
    app.run(debug=True)
