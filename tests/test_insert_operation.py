import pytest
from adjacency_matrix import AdjacencyMatrix
from dependencies import (
    TemporalDependency,
    ExistentialDependency,
    TemporalType,
    ExistentialType,
    Direction,
)
from change_operations.insert_operation import insert_activity
from utils.check_contradictions import has_existential_contradiction, has_temporal_contradiction, _dfs



def test_insert_activity_direct_temp():
    matrix = AdjacencyMatrix(activities=["A", "B"])
    matrix.add_dependency(
        "A", "B",
        TemporalDependency(TemporalType.DIRECT, Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )

    expected_result_matrix = AdjacencyMatrix(activities=["A", "B", "C"])
    expected_result_matrix.add_dependency(
        "A", "B",
        TemporalDependency(TemporalType.EVENTUAL, Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    expected_result_matrix.add_dependency(
        "A", "C",
        TemporalDependency(TemporalType.DIRECT, Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    expected_result_matrix.add_dependency(
        "C", "B",
        TemporalDependency(TemporalType.DIRECT, Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    expected_result_matrix.add_dependency(
        "B", "A",
        TemporalDependency(TemporalType.EVENTUAL, Direction.BACKWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    expected_result_matrix.add_dependency(
        "C", "A",
        TemporalDependency(TemporalType.DIRECT, Direction.BACKWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    expected_result_matrix.add_dependency(
        "B", "C",
        TemporalDependency(TemporalType.DIRECT, Direction.BACKWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    
    
    assert insert_activity(matrix, "C", {
        ("A", "C"): (TemporalDependency(TemporalType.DIRECT, Direction.FORWARD), ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH))}) == expected_result_matrix


def test_insert_activity_end():
    matrix = AdjacencyMatrix(activities=["A", "B"])
    matrix.add_dependency(
        "A", "B",
        TemporalDependency(TemporalType.DIRECT, Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )

    expected_result_matrix = AdjacencyMatrix(activities=["A", "B", "C"])
    expected_result_matrix.add_dependency(
        "A", "B",
        TemporalDependency(TemporalType.DIRECT, Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    expected_result_matrix.add_dependency(
        "A", "C",
        TemporalDependency(TemporalType.EVENTUAL, Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    expected_result_matrix.add_dependency(
        "B", "C",
        TemporalDependency(TemporalType.DIRECT, Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    expected_result_matrix.add_dependency(
        "B", "A",
        TemporalDependency(TemporalType.DIRECT, Direction.BACKWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    expected_result_matrix.add_dependency(
        "C", "A",
        TemporalDependency(TemporalType.EVENTUAL, Direction.BACKWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    expected_result_matrix.add_dependency(
        "C", "B",
        TemporalDependency(TemporalType.DIRECT, Direction.BACKWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    
    
    assert insert_activity(matrix, "C", {
        ("B", "C"): (TemporalDependency(TemporalType.DIRECT, Direction.FORWARD), ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH))}) == expected_result_matrix


def test_insert_in_empty_process():
    # Create empty matrix
    matrix = AdjacencyMatrix(activities=[])
    
    # Create result with activity in it
    expected_result_matrix = AdjacencyMatrix(activities=["A"])
    
    assert insert_activity(matrix, "A", {}) == expected_result_matrix

def test_has_existential_contradiction():
    deps = {
        ('A', 'B'): (None, ExistentialDependency(ExistentialType.NEGATED_EQUIVALENCE, Direction.BOTH)),
        ('B', 'C'): (None, ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)),
        ('C', 'A'): (None, ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)),
    }
    assert has_existential_contradiction(deps) is True
    deps = {
        ('A', 'B'): (None, ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)),
        ('B', 'C'): (None, ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)),
        ('C', 'A'): (None, ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)),
    }
    assert has_existential_contradiction(deps) is False

def test_has_temporal_contradiction():
    temporal_deps = {
        ('A', 'B'): TemporalDependency(TemporalType.DIRECT, Direction.FORWARD),
        ('B', 'C'): TemporalDependency(TemporalType.DIRECT, Direction.FORWARD),
        ('C', 'A'): TemporalDependency(TemporalType.DIRECT, Direction.FORWARD),
    }
    existential_deps = {}
    activities = ["A", "B", "C"]
    assert has_temporal_contradiction(temporal_deps, existential_deps, activities, "B", ["A", "B", "C"]) is True

def test_has_temporal_loop():
    activities = ["A", "B", "C", "D"]
    temporal_deps = {
        ('A', 'B'): TemporalDependency(TemporalType.DIRECT, Direction.FORWARD),
        ('A', 'C'): TemporalDependency(TemporalType.EVENTUAL, Direction.FORWARD),
        ('A', 'D'): TemporalDependency(TemporalType.EVENTUAL, Direction.FORWARD),
        ('B', 'A'): TemporalDependency(TemporalType.DIRECT, Direction.BACKWARD),
        ('B', 'C'): TemporalDependency(TemporalType.EVENTUAL, Direction.FORWARD),
        ('B', 'D'): TemporalDependency(TemporalType.EVENTUAL, Direction.FORWARD),
        ('C', 'A'): TemporalDependency(TemporalType.EVENTUAL, Direction.BACKWARD),
        ('C', 'B'): TemporalDependency(TemporalType.EVENTUAL, Direction.BACKWARD),
        ('C', 'D'): TemporalDependency(TemporalType.INDEPENDENCE, Direction.BOTH),
        ('D', 'C'): TemporalDependency(TemporalType.INDEPENDENCE, Direction.BOTH),
        ('D', 'A'): TemporalDependency(TemporalType.EVENTUAL, Direction.BACKWARD),
        ('D', 'B'): TemporalDependency(TemporalType.EVENTUAL, Direction.BACKWARD),
    }
    for activity in activities:
        _dfs(temporal_deps, activity, set(), set())