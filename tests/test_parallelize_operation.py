import pytest
from dependencies import TemporalDependency, TemporalType, ExistentialDependency, ExistentialType
from adjacency_matrix import AdjacencyMatrix
from change_operations.parallelize_operation import parallelize_activities, parallelize_activities_on_variants

def test_parallelize_variants():
    variants = [["A", "B"]]
    dependencies = {
        ("A", "B"):
        (TemporalDependency(TemporalType.DIRECT), ExistentialDependency(ExistentialType.EQUIVALENCE))
        }

    expected = [["A", "B"], ["B", "A"]]
    actual = parallelize_activities_on_variants(set(["A", "B"]), dependencies, variants)

    # Sort inner lists and then sort the outer list
    expected_sorted = sorted([sorted(lst) for lst in expected])
    actual_sorted = sorted([sorted(lst) for lst in actual])

    assert expected_sorted == actual_sorted

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
        None,
        ExistentialDependency(ExistentialType.EQUIVALENCE)
    )
    result_matrix.add_dependency(
        "B", "A",
        None,
        ExistentialDependency(ExistentialType.EQUIVALENCE)
    )

    assert parallelize_activities(matrix, set(["A", "B"])) == result_matrix