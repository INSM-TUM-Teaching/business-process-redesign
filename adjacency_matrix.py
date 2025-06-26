from dataclasses import dataclass
import yaml
from typing import Dict, Tuple, List, Optional
from dependencies import (
    TemporalDependency,
    ExistentialDependency,
    TemporalType,
    ExistentialType,
)


@dataclass
class AdjacencyMatrix:
    """
    Represents an adjacency matrix for process activities,
    mapping pairs of activities to their temporal and existential dependencies.
    """

    dependencies: Dict[
        Tuple[str, str],
        Tuple[Optional[TemporalDependency], Optional[ExistentialDependency]],
    ]
    activities: List[str]

    def __init__(self, activities: List[str]):
        self.activities = activities
        self.dependencies = {}

    def add_dependency(
        self,
        from_activity: str,
        to_activity: str,
        temporal_dep: Optional[TemporalDependency],
        existential_dep: Optional[ExistentialDependency],
    ):
        """Adds a dependency to the matrix."""
        if from_activity not in self.activities or to_activity not in self.activities:
            raise ValueError("Activities must be in the predefined list of activities.")
        self.dependencies[(from_activity, to_activity)] = (
            temporal_dep,
            existential_dep,
        )

    def get_dependency(
        self, from_activity: str, to_activity: str
    ) -> Optional[Tuple[Optional[TemporalDependency], Optional[ExistentialDependency]]]:
        """Retrieves the dependency between two activities."""
        return self.dependencies.get((from_activity, to_activity))


def parse_yaml_to_adjacency_matrix(file_path: str) -> AdjacencyMatrix:
    """
    Parses a YAML file defining process dependencies into an AdjacencyMatrix.
    """
    with open(file_path, "r") as f:
        data = yaml.safe_load(f)

    metadata = data.get("metadata", {})
    activities = metadata.get("activities", [])
    if not activities:
        raise ValueError("YAML file must define a list of activities in metadata.")

    matrix = AdjacencyMatrix(activities=activities)

    yaml_dependencies = data.get("dependencies", [])
    for dep in yaml_dependencies:
        from_activity = dep.get("from")
        to_activity = dep.get("to")

        if not from_activity or not to_activity:
            raise ValueError("Each dependency must specify 'from' and 'to' activities.")

        temporal_data = dep.get("temporal")
        temporal_dep_obj = None
        if temporal_data and temporal_data.get("type"):
            try:
                ttype = TemporalType.from_yaml(temporal_data["type"])
                temporal_dep_obj = TemporalDependency(type=ttype)
            except ValueError as e:
                print(
                    f"Warning: Skipping temporal dependency for ({from_activity}, {to_activity}) due to unknown type: {e}"
                )

        existential_data = dep.get("existential")
        existential_dep_obj = None
        if existential_data and existential_data.get("type"):
            try:
                etype = ExistentialType.from_yaml(existential_data["type"])
                existential_dep_obj = ExistentialDependency(type=etype)
            except ValueError as e:
                print(
                    f"Warning: Skipping existential dependency for ({from_activity}, {to_activity}) due to unknown type: {e}"
                )

        matrix.add_dependency(
            from_activity, to_activity, temporal_dep_obj, existential_dep_obj
        )

    return matrix


def write_adjacency_matrix_to_yaml(matrix: AdjacencyMatrix, file_path: str):
    """
    Serializes an AdjacencyMatrix object into a YAML file with formatting and symbols.
    """
    mapping_temporal = {
        TemporalType.DIRECT: ("direct", "≺_d"),
        TemporalType.EVENTUAL: ("eventual", "≺_e"),
        TemporalType.INDEPENDENCE: ("independence", "-"),
    }

    mapping_existential = {
        ExistentialType.IMPLICATION: ("implication", "⇒"),
        ExistentialType.EQUIVALENCE: ("equivalence", "⇔"),
        ExistentialType.NEGATED_EQUIVALENCE: ("negated equivalence", "⇎"),
        ExistentialType.NAND: ("nand", "|"),
        ExistentialType.OR: ("or", "∨"),
        ExistentialType.INDEPENDENCE: ("independence", "-"),
    }

    data = {
        "metadata": {
            "format_version": "1.0",
            "description": "Process adjacency matrix with temporal and existential dependencies",
            "activities": matrix.activities,
        },
        "dependencies": []
    }

    for (from_activity, to_activity), (temporal, existential) in matrix.dependencies.items():
        dep_entry = {
            "from": from_activity,
            "to": to_activity,
        }

        if temporal:
            temporal_type, temporal_symbol = mapping_temporal[temporal.type]
            dep_entry["temporal"] = {
                "type": temporal_type,
                "symbol": temporal_symbol,
            }

        if existential:
            existential_type, existential_symbol = mapping_existential[existential.type]
            dep_entry["existential"] = {
                "type": existential_type,
                "symbol": existential_symbol,
            }

        data["dependencies"].append(dep_entry)

    with open(file_path, "w") as f:
        yaml.dump(data, f, sort_keys=False, default_flow_style=False)