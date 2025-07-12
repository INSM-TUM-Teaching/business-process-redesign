import pytest
from adjacency_matrix import AdjacencyMatrix
from dependencies import (
    TemporalDependency,
    ExistentialDependency,
    TemporalType,
    ExistentialType,
    Direction,
)
from change_operations.move_operation import move_activity

def test_move_activity_direct_temp():
    matrix = AdjacencyMatrix(activities=["A", "B", "C"])
    matrix.add_dependency(
        "A", "B",
        TemporalDependency(TemporalType.DIRECT, Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    matrix.add_dependency(
        "A", "C",
        TemporalDependency(TemporalType.EVENTUAL, Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    matrix.add_dependency(
        "B", "C",
        TemporalDependency(TemporalType.DIRECT, Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    matrix.add_dependency(
        "B", "A",
        TemporalDependency(TemporalType.DIRECT, Direction.BACKWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    matrix.add_dependency(
        "C", "A",
        TemporalDependency(TemporalType.EVENTUAL, Direction.BACKWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    matrix.add_dependency(
        "C", "B",
        TemporalDependency(TemporalType.DIRECT, Direction.BACKWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )

    expected_result_matrix = AdjacencyMatrix(activities=["A", "B", "C"])
    expected_result_matrix.add_dependency(
        "B", "C",
        TemporalDependency(TemporalType.DIRECT, Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    expected_result_matrix.add_dependency(
        "C", "A",
        TemporalDependency(TemporalType.DIRECT, Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    expected_result_matrix.add_dependency(
        "B", "A",
        TemporalDependency(TemporalType.EVENTUAL, Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    expected_result_matrix.add_dependency(
        "C", "B",
        TemporalDependency(TemporalType.DIRECT, Direction.BACKWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    expected_result_matrix.add_dependency(
        "A", "C",
        TemporalDependency(TemporalType.DIRECT, Direction.BACKWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    expected_result_matrix.add_dependency(
        "A", "B",
        TemporalDependency(TemporalType.EVENTUAL, Direction.BACKWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    
    
    assert move_activity(matrix, "A", {("C", "A"): (TemporalDependency(TemporalType.DIRECT, Direction.FORWARD), ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH))}) == expected_result_matrix