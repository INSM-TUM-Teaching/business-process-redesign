import pytest
from dependencies import TemporalDependency, TemporalType, ExistentialDependency, ExistentialType
from adjacency_matrix import AdjacencyMatrix
from change_operations.parallelize_operation import parallelize_activities

def test_parallelize_activities():
    matrix = AdjacencyMatrix(activities=["A", "B"])
    matrix.add_dependency(
        "A", "B",
        TemporalDependency(TemporalType.DIRECT),
        ExistentialDependency(ExistentialType.EQUIVALENCE)
    )
    result_matrix = AdjacencyMatrix(activities=["A", "B"])
    result_matrix.add_dependency(
        "A", "B",
        TemporalDependency(TemporalType.INDEPENDENCE),
        ExistentialDependency(ExistentialType.EQUIVALENCE)
    )
    result_matrix.add_dependency(
        "B", "A",
        TemporalDependency(TemporalType.INDEPENDENCE),
        ExistentialDependency(ExistentialType.EQUIVALENCE)
    )

    assert parallelize_activities(matrix, set(["A", "B"])) == result_matrix


