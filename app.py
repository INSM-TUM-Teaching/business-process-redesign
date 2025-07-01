import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, jsonify
from traces_to_matrix import traces_to_adjacency_matrix
from change_operations.delete_operation import delete_activity
from dependencies import TemporalType, ExistentialType
import traceback

app = Flask(__name__)

# Global variable to store current matrix (in a real app, use session or database)
current_matrix = None


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/api/analyze-traces", methods=["POST"])
def analyze_traces():
    """Analyze process traces and return discovered dependencies"""
    try:
        data = request.get_json()
        traces = data.get("traces", [])
        temporal_threshold = data.get("temporal_threshold", 1.0)
        existential_threshold = data.get("existential_threshold", 1.0)

        if not traces:
            return jsonify({"success": False, "error": "No traces provided"})

        # Generate adjacency matrix using the existing algorithm
        global current_matrix
        current_matrix = traces_to_adjacency_matrix(
            traces,
            temporal_threshold=temporal_threshold,
            existential_threshold=existential_threshold,
        )

        # Extract activities
        activities = current_matrix.activities

        # Extract dependencies for display
        dependencies = []
        for from_activity in activities:
            for to_activity in activities:
                if from_activity != to_activity:
                    dep_tuple = current_matrix.get_dependency(
                        from_activity, to_activity
                    )
                    if dep_tuple:
                        temporal_dep, existential_dep = dep_tuple

                        if temporal_dep:
                            dep_type = "Temporal"
                            if temporal_dep.type == TemporalType.DIRECT:
                                subtype = "Direct"
                            elif temporal_dep.type == TemporalType.EVENTUAL:
                                subtype = "Eventual"
                            else:
                                subtype = "Independence"

                            dependencies.append(
                                {
                                    "from": from_activity,
                                    "to": to_activity,
                                    "type": dep_type,
                                    "subtype": subtype,
                                }
                            )

                        if existential_dep:
                            dep_type = "Existential"
                            if existential_dep.type == ExistentialType.IMPLICATION:
                                subtype = "Implication"
                            elif existential_dep.type == ExistentialType.EQUIVALENCE:
                                subtype = "Equivalence"
                            elif (
                                existential_dep.type
                                == ExistentialType.NEGATED_EQUIVALENCE
                            ):
                                subtype = "Negated Equivalence"
                            elif existential_dep.type == ExistentialType.NAND:
                                subtype = "NAND"
                            elif existential_dep.type == ExistentialType.OR:
                                subtype = "OR"
                            else:
                                subtype = "Independence"

                            dependencies.append(
                                {
                                    "from": from_activity,
                                    "to": to_activity,
                                    "type": dep_type,
                                    "subtype": subtype,
                                }
                            )

        return jsonify(
            {
                "success": True,
                "results": {
                    "trace_count": len(traces),
                    "activities": activities,
                    "dependencies": dependencies,
                },
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/generate-matrix", methods=["POST"])
def generate_matrix():
    """Generate and return the adjacency matrix"""
    try:
        data = request.get_json()
        traces = data.get("traces", [])
        temporal_threshold = data.get("temporal_threshold", 1.0)
        existential_threshold = data.get("existential_threshold", 1.0)

        if not traces:
            return jsonify({"success": False, "error": "No traces provided"})

        # Generate matrix if not already done
        global current_matrix
        if current_matrix is None:
            current_matrix = traces_to_adjacency_matrix(
                traces,
                temporal_threshold=temporal_threshold,
                existential_threshold=existential_threshold,
            )

        # Extract activities and dependencies for matrix display
        activities = current_matrix.activities
        dependencies = []

        for from_activity in activities:
            for to_activity in activities:
                if from_activity != to_activity:
                    dep_tuple = current_matrix.get_dependency(
                        from_activity, to_activity
                    )
                    if dep_tuple:
                        temporal_dep, existential_dep = dep_tuple

                        dep_type = None
                        if temporal_dep:
                            if temporal_dep.type == TemporalType.DIRECT:
                                dep_type = "Direct"
                            elif temporal_dep.type == TemporalType.EVENTUAL:
                                dep_type = "Eventual"
                        elif existential_dep:
                            if existential_dep.type == ExistentialType.IMPLICATION:
                                dep_type = "Implication"
                            elif existential_dep.type == ExistentialType.EQUIVALENCE:
                                dep_type = "Equivalence"
                            # Add other existential types as needed

                        if dep_type:
                            dependencies.append(
                                {
                                    "from": from_activity,
                                    "to": to_activity,
                                    "type": dep_type,
                                }
                            )

        return jsonify(
            {
                "success": True,
                "matrix": {"activities": activities, "dependencies": dependencies},
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/delete-activity", methods=["POST"])
def delete_activity_endpoint():
    """Delete an activity from the current matrix"""
    try:
        data = request.get_json()
        activity = data.get("activity")
        preserve_incoming = data.get("preserve_incoming", True)
        preserve_outgoing = data.get("preserve_outgoing", True)

        if not activity:
            return jsonify({"success": False, "error": "No activity specified"})

        global current_matrix
        if current_matrix is None:
            return jsonify(
                {
                    "success": False,
                    "error": "No matrix available. Please analyze traces first.",
                }
            )

        # Check if activity exists
        if activity not in current_matrix.activities:
            return jsonify(
                {
                    "success": False,
                    "error": f"Activity '{activity}' not found in matrix",
                }
            )

        # Apply delete operation
        modified_matrix = delete_activity(current_matrix, activity)

        # Update current matrix
        current_matrix = modified_matrix

        return jsonify(
            {
                "success": True,
                "message": f"Successfully deleted activity '{activity}' from matrix",
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/matrix-status", methods=["GET"])
def matrix_status():
    """Get current matrix status"""
    global current_matrix
    if current_matrix is None:
        return jsonify({"has_matrix": False})

    activities = current_matrix.activities
    return jsonify(
        {
            "has_matrix": True,
            "activity_count": len(activities),
            "activities": activities,
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
