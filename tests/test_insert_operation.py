import pytest
from adjacency_matrix import AdjacencyMatrix
from dependencies import (
    TemporalDependency,
    ExistentialDependency,
    TemporalType,
    ExistentialType,
)
from change_operations.insert_operation import insert_activity

#What is intendet behaviour for this?:
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


def test_insert_activity():
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
        ("B", "C"): (TemporalDependency(TemporalType.DIRECT), ExistentialDependency(ExistentialType.EQUIVALENCE))}) == expected_result_matrix


def test_insert_in_empty_process():
    # Create matrix with A->B where A and B are equivalent
    matrix = AdjacencyMatrix(activities=[])
    
    expected_result_matrix = AdjacencyMatrix(activities=["A"])
    # Deleting either A or B should fail as it would result in empty process
    # due to equivalence relationship
    
    assert insert_activity(matrix, "A", {}) == expected_result_matrix
