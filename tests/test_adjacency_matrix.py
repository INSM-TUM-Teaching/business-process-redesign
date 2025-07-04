import pytest
from adjacency_matrix import parse_yaml_to_adjacency_matrix, AdjacencyMatrix
from dependencies import TemporalType, ExistentialType, Direction

def test_parse_yaml_to_adjacency_matrix_first_prototype(capsys):
    yaml_file_path = "sample-matrices/first_prototype.yaml"
    adj_matrix = parse_yaml_to_adjacency_matrix(yaml_file_path)

    print(f"Successfully parsed activities: {adj_matrix.activities}")
    # Sort dependencies for consistent output
    sorted_dependencies = sorted(adj_matrix.dependencies.items())

    for (act_from, act_to), (temp_dep, exist_dep) in sorted_dependencies:
        print(f"Dependency from {act_from} to {act_to}:")
        if temp_dep:
            print(f"  Temporal: {temp_dep.type.name} ({temp_dep.direction.name})")
        else:
            print(f"  Temporal: None")
        if exist_dep:
            print(
                f"  Existential: {exist_dep.type.name} ({exist_dep.direction.name})"
            )
        else:
            print(f"  Existential: None")

    captured = capsys.readouterr()
    expected_output = """Successfully parsed activities: ['A', 'B', 'C', 'D', 'E']
Dependency from A to B:
  Temporal: DIRECT (FORWARD)
  Existential: IMPLICATION (FORWARD)
Dependency from B to C:
  Temporal: EVENTUAL (FORWARD)
  Existential: EQUIVALENCE (BOTH)
Dependency from C to D:
  Temporal: INDEPENDENCE (BOTH)
  Existential: NAND (BOTH)
Dependency from D to E:
  Temporal: DIRECT (FORWARD)
  Existential: INDEPENDENCE (BOTH)
"""
    assert captured.out.strip() == expected_output.strip()
    
def test_parse_yaml_value_error_missing_activities():
    # Create a dummy yaml file with missing activities
    content = """
dependencies:
  - from: A
    to: B
"""
    with open("test_missing_activities.yaml", "w") as f:
        f.write(content)
    
    with pytest.raises(ValueError) as excinfo:
        parse_yaml_to_adjacency_matrix("test_missing_activities.yaml")
    assert "YAML file must define a list of activities in metadata." in str(excinfo.value)
    # Clean up the dummy file
    import os
    os.remove("test_missing_activities.yaml")

def test_parse_yaml_value_error_missing_from_to():
    # Create a dummy yaml file with missing from/to in dependencies
    content = """
metadata:
  activities: [A, B]
dependencies:
  - to: B # Missing 'from'
"""
    with open("test_missing_from_to.yaml", "w") as f:
        f.write(content)

    with pytest.raises(ValueError) as excinfo:
        parse_yaml_to_adjacency_matrix("test_missing_from_to.yaml")
    assert "Each dependency must specify 'from' and 'to' activities." in str(excinfo.value)
    # Clean up the dummy file
    import os
    os.remove("test_missing_from_to.yaml")

