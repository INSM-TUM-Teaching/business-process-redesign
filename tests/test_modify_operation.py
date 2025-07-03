import pytest
from adjacency_matrix import AdjacencyMatrix
from dependencies import (
    TemporalDependency,
    ExistentialDependency,
    TemporalType,
    ExistentialType,
)
from change_operations.modify_operation import modify_dependency


def test_modify_dependency():  
    # Create a simple matrix with A < B < C dependencies
    matrix = AdjacencyMatrix(activities=["A", "B", "C"])
    
    # define the matrix with dependencies 
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
        "B", "A",
        TemporalDependency(TemporalType.DIRECT),
        ExistentialDependency(ExistentialType.EQUIVALENCE)
    )
    matrix.add_dependency(
        "B", "C",
        TemporalDependency(TemporalType.DIRECT),
        ExistentialDependency(ExistentialType.EQUIVALENCE)
    )
    matrix.add_dependency(
        "C", "A",
        TemporalDependency(TemporalType.EVENTUAL),
        ExistentialDependency(ExistentialType.EQUIVALENCE)
    )
    matrix.add_dependency(
        "C", "B",
        TemporalDependency(TemporalType.EVENTUAL),
        ExistentialDependency(ExistentialType.EQUIVALENCE)
    )

    # create comparison matrix which we use to check the change operation 
    expected_matrix = AdjacencyMatrix(activities=["A", "B", "C"])
    
    # define the matrix with dependencies 
    expected_matrix.add_dependency(
        "A", "B",
        TemporalDependency(TemporalType.DIRECT),
        ExistentialDependency(ExistentialType.NEGATED_EQUIVALENCE)
    )
    expected_matrix.add_dependency(
        "A", "C",
        TemporalDependency(TemporalType.EVENTUAL),
        ExistentialDependency(ExistentialType.EQUIVALENCE)
    )
    expected_matrix.add_dependency(
        "B", "A",
        TemporalDependency(TemporalType.DIRECT),
        ExistentialDependency(ExistentialType.NEGATED_EQUIVALENCE)
    )
    expected_matrix.add_dependency(
        "B", "C",
        TemporalDependency(TemporalType.DIRECT),
        ExistentialDependency(ExistentialType.EQUIVALENCE)
    )
    expected_matrix.add_dependency(
        "C", "A",
        TemporalDependency(TemporalType.EVENTUAL),
        ExistentialDependency(ExistentialType.EQUIVALENCE)
    )
    expected_matrix.add_dependency(
        "C", "B",
        TemporalDependency(TemporalType.EVENTUAL),
        ExistentialDependency(ExistentialType.EQUIVALENCE)
    )

    # perform the test whether the function returns the expected matrix 
    assert modify_dependency(matrix, "A", "B", None, ExistentialType.NEGATED_EQUIVALENCE) == expected_matrix