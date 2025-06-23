from typing import Tuple, Dict
import pytest
from adjacency_matrix import AdjacencyMatrix
from dependencies import (
    TemporalDependency,
    ExistentialDependency,
    TemporalType,
    ExistentialType,
)
from change_operations.insert_operation import (
    insert_activity,
    determine_set_before,
    determine_set_after,
    has_existential_contradiction,
    has_temporal_contradiction
    )


def test_insert_activity_direct_temp():
    matrix = AdjacencyMatrix(activities=["A", "B"])
    matrix.add_dependency(
        "A", "B",
        TemporalDependency(TemporalType.DIRECT),
        ExistentialDependency(ExistentialType.EQUIVALENCE)
    )

    expected_result_matrix = AdjacencyMatrix(activities=["A", "B", "C"])
    expected_result_matrix.add_dependency(
        "A", "B",
        TemporalDependency(TemporalType.EVENTUAL),
        ExistentialDependency(ExistentialType.EQUIVALENCE)
    )
    expected_result_matrix.add_dependency(
        "A", "C",
        TemporalDependency(TemporalType.DIRECT),
        ExistentialDependency(ExistentialType.EQUIVALENCE)
    )
    expected_result_matrix.add_dependency(
        "C", "B",
        TemporalDependency(TemporalType.DIRECT),
        ExistentialDependency(ExistentialType.EQUIVALENCE)
    )
    expected_result_matrix.add_dependency(
        "B", "A",
        None,
        ExistentialDependency(ExistentialType.EQUIVALENCE)
    )
    expected_result_matrix.add_dependency(
        "C", "A",
        None,
        ExistentialDependency(ExistentialType.EQUIVALENCE)
    )
    expected_result_matrix.add_dependency(
        "B", "C",
        None,
        ExistentialDependency(ExistentialType.EQUIVALENCE)
    )
    
    
    assert insert_activity(matrix, "C", {
        ("A", "C"): (TemporalDependency(TemporalType.DIRECT), ExistentialDependency(ExistentialType.EQUIVALENCE))}) == expected_result_matrix


def test_insert_activity_end():
    matrix = AdjacencyMatrix(activities=["A", "B"])
    matrix.add_dependency(
        "A", "B",
        TemporalDependency(TemporalType.DIRECT),
        ExistentialDependency(ExistentialType.EQUIVALENCE)
    )

    expected_result_matrix = AdjacencyMatrix(activities=["A", "B", "C"])
    expected_result_matrix.add_dependency(
        "A", "B",
        TemporalDependency(TemporalType.DIRECT),
        ExistentialDependency(ExistentialType.EQUIVALENCE)
    )
    expected_result_matrix.add_dependency(
        "A", "C",
        TemporalDependency(TemporalType.EVENTUAL),
        ExistentialDependency(ExistentialType.EQUIVALENCE)
    )
    expected_result_matrix.add_dependency(
        "B", "C",
        TemporalDependency(TemporalType.DIRECT),
        ExistentialDependency(ExistentialType.EQUIVALENCE)
    )
    expected_result_matrix.add_dependency(
        "B", "A",
        None,
        ExistentialDependency(ExistentialType.EQUIVALENCE)
    )
    expected_result_matrix.add_dependency(
        "C", "A",
        None,
        ExistentialDependency(ExistentialType.EQUIVALENCE)
    )
    expected_result_matrix.add_dependency(
        "C", "B",
        None,
        ExistentialDependency(ExistentialType.EQUIVALENCE)
    )
    
    
    assert insert_activity(matrix, "C", {
        ("B", "C"): (TemporalDependency(TemporalType.EVENTUAL), ExistentialDependency(ExistentialType.EQUIVALENCE))}) == expected_result_matrix


def test_insert_in_empty_process():
    # Create empty matrix
    matrix = AdjacencyMatrix(activities=[])
    
    # Create result with activity in it
    expected_result_matrix = AdjacencyMatrix(activities=["A"])
    
    assert insert_activity(matrix, "A", {}) == expected_result_matrix

def test_determine_set_before():
    temporal_deps: Dict[Tuple[str, str], TemporalDependency] = {}
    temporal_deps[("A", "B")] = TemporalDependency(TemporalType.DIRECT)
    temporal_deps[("B", "C")] = TemporalDependency(TemporalType.DIRECT)
    temporal_deps[("C", "D")] = TemporalDependency(TemporalType.EVENTUAL)
    temporal_deps[("E", "D")] = TemporalDependency(TemporalType.INDEPENDENCE)
    assert determine_set_before(temporal_deps, "C", set()) == set(["A", "B"])

def test_determine_set_after():
    temporal_deps: Dict[Tuple[str, str], TemporalDependency] = {}
    temporal_deps[("A", "B")] = TemporalDependency(TemporalType.DIRECT)
    temporal_deps[("B", "C")] = TemporalDependency(TemporalType.DIRECT)
    temporal_deps[("C", "D")] = TemporalDependency(TemporalType.EVENTUAL)
    temporal_deps[("E", "D")] = TemporalDependency(TemporalType.INDEPENDENCE)
    assert determine_set_after(temporal_deps, "A", set()) == set(["C", "B", "D"])

def test_has_existential_contradiction():
    deps = {
        ('A', 'B'): ExistentialDependency(ExistentialType.NEGATED_EQUIVALENCE),
        ('B', 'C'): ExistentialDependency(ExistentialType.EQUIVALENCE),
        ('C', 'A'): ExistentialDependency(ExistentialType.EQUIVALENCE),
    }
    assert has_existential_contradiction(deps) == True
    deps = {
        ('A', 'B'): ExistentialDependency(ExistentialType.EQUIVALENCE),
        ('B', 'C'): ExistentialDependency(ExistentialType.EQUIVALENCE),
        ('C', 'A'): ExistentialDependency(ExistentialType.EQUIVALENCE),
    }
    assert has_existential_contradiction(deps) == False

def test_has_temporal_contradiction():
    deps = {
        ('A', 'B'): TemporalDependency(TemporalType.DIRECT),
        ('B', 'C'): TemporalDependency(TemporalType.DIRECT),
        ('C', 'A'): TemporalDependency(TemporalType.DIRECT),
    }
    activities = ["A", "B", "C"]
    assert has_temporal_contradiction(deps, activities, "B", ["A", "B", "C"]) == True