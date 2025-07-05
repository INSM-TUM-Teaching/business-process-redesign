import pytest
from adjacency_matrix import AdjacencyMatrix
from dependencies import (
    TemporalDependency,
    ExistentialDependency,
    TemporalType,
    ExistentialType,
    Direction,
)
from change_operations.modify_operation import modify_dependency


def test_modify_dependency():  
    # Create a simple matrix with A < B < C dependencies
    matrix = AdjacencyMatrix(activities=["A", "B", "C"])
    
    # define the matrix with dependencies 
    matrix.add_dependency(
        "A", "B",
        TemporalDependency(TemporalType.DIRECT, direction=Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, direction=Direction.BOTH)
    )
    matrix.add_dependency(
        "A", "C",
        TemporalDependency(TemporalType.EVENTUAL, direction=Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, direction=Direction.BOTH)
    )
    matrix.add_dependency(
        "B", "A",
        TemporalDependency(TemporalType.DIRECT, direction=Direction.BACKWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, direction=Direction.BOTH)
    )
    matrix.add_dependency(
        "B", "C",
        TemporalDependency(TemporalType.DIRECT, direction=Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, direction=Direction.BOTH)
    )
    matrix.add_dependency(
        "C", "A",
        TemporalDependency(TemporalType.EVENTUAL, direction=Direction.BACKWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, direction=Direction.BOTH)
    )
    matrix.add_dependency(
        "C", "B",
        TemporalDependency(TemporalType.EVENTUAL, direction=Direction.BACKWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, direction=Direction.BOTH)
    )

    # create comparison matrix which we use to check the change operation 
    expected_matrix = AdjacencyMatrix(activities=["A", "B", "C"])
    
    # define the matrix with dependencies 
    expected_matrix.add_dependency(
        "A", "B",
        TemporalDependency(TemporalType.DIRECT, direction=Direction.FORWARD),
        ExistentialDependency(ExistentialType.NEGATED_EQUIVALENCE, direction=Direction.BOTH)
    )
    expected_matrix.add_dependency(
        "A", "C",
        TemporalDependency(TemporalType.EVENTUAL, direction=Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, direction=Direction.BOTH)
    )
    expected_matrix.add_dependency(
        "B", "A",
        TemporalDependency(TemporalType.DIRECT, direction=Direction.BACKWARD),
        ExistentialDependency(ExistentialType.NEGATED_EQUIVALENCE, direction=Direction.BOTH)
    )
    expected_matrix.add_dependency(
        "B", "C",
        TemporalDependency(TemporalType.DIRECT, direction=Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, direction=Direction.BOTH)
    )
    expected_matrix.add_dependency(
        "C", "A",
        TemporalDependency(TemporalType.EVENTUAL, direction=Direction.BACKWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, direction=Direction.BOTH)
    )
    expected_matrix.add_dependency(
        "C", "B",
        TemporalDependency(TemporalType.EVENTUAL, direction=Direction.BACKWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, direction=Direction.BOTH)
    )

    # perform the test whether the function returns the expected matrix 
    assert modify_dependency(matrix, "A", "B", None, ExistentialType.NEGATED_EQUIVALENCE) == expected_matrix