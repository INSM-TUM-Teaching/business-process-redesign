import pytest
from adjacency_matrix import AdjacencyMatrix
from dependencies import (
    TemporalDependency,
    ExistentialDependency,
    TemporalType,
    ExistentialType,
    Direction,
)
from change_operations.replace_operation import replace_activity

def test_replace_activity():
    # Create a simple matrix with A<->B<->C dependencies, forming a sequence of activities 
    matrix = AdjacencyMatrix(activities=["A", "B", "C"])
    matrix.add_dependency(
        "A", "B",
        TemporalDependency(TemporalType.DIRECT, direction=Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, direction=Direction.BOTH)
    )
    matrix.add_dependency(
        "B", "C",
        TemporalDependency(TemporalType.DIRECT, direction=Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, direction=Direction.BOTH)
    )
    matrix.add_dependency(
        "A", "C",
        TemporalDependency(TemporalType.EVENTUAL, direction=Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, direction=Direction.BOTH)
    )
    
    # Delete activity B
    new_matrix = replace_activity(matrix, "A", "X")
    
    # Check that A is replaced with activity X 
    assert "A" not in new_matrix.activities
    assert set(new_matrix.activities) == {"B", "C", "X"}