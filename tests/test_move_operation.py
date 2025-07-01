import pytest
from adjacency_matrix import AdjacencyMatrix
from dependencies import (
    TemporalDependency,
    ExistentialDependency,
    TemporalType,
    ExistentialType,
)
from change_operations.move_operation import move_activity

def test_move_activity_direct_temp():
    matrix = AdjacencyMatrix(activities=["A", "B", "C"])
    matrix.add_dependency(
        "A", "B",
        TemporalDependency(TemporalType.DIRECT),
        ExistentialDependency(ExistentialType.EQUIVALENCE)
    )
    matrix.add_dependency(
        "A", "C",
        TemporalDependency(TemporalType.EVENTUAL),
        ExistentialDependency(ExistentialType.EQUIVALENCE)
    )
    matrix.add_dependency(
        "B", "C",
        TemporalDependency(TemporalType.DIRECT),
        ExistentialDependency(ExistentialType.EQUIVALENCE)
    )

    expected_result_matrix = AdjacencyMatrix(activities=["A", "B", "C"])
    expected_result_matrix.add_dependency(
        "B", "C",
        TemporalDependency(TemporalType.DIRECT),
        ExistentialDependency(ExistentialType.EQUIVALENCE)
    )
    expected_result_matrix.add_dependency(
        "C", "A",
        TemporalDependency(TemporalType.DIRECT),
        ExistentialDependency(ExistentialType.EQUIVALENCE)
    )
    expected_result_matrix.add_dependency(
        "B", "A",
        TemporalDependency(TemporalType.EVENTUAL),
        ExistentialDependency(ExistentialType.EQUIVALENCE)
    )
    expected_result_matrix.add_dependency(
        "A", "B",
        None,
        ExistentialDependency(ExistentialType.EQUIVALENCE)
    )
    expected_result_matrix.add_dependency(
        "A", "C",
        None,
        ExistentialDependency(ExistentialType.EQUIVALENCE)
    )
    expected_result_matrix.add_dependency(
        "C", "B",
        None,
        ExistentialDependency(ExistentialType.EQUIVALENCE)
    )
    
    
    assert move_activity(matrix, "A", {("C", "A"): (TemporalDependency(TemporalType.DIRECT), ExistentialDependency(ExistentialType.EQUIVALENCE))}) == expected_result_matrix