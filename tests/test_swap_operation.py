import pytest
from adjacency_matrix import AdjacencyMatrix
from dependencies import (
    TemporalDependency,
    ExistentialDependency,
    TemporalType,
    ExistentialType,
)
from change_operations.swap_operation import swap_activities, swap_activities_in_variants

def test_swap_activities_in_variants():
    variants = [["A", "B", "C"], ["A", "C", "B"]]
    swapped = swap_activities_in_variants(variants, "A", "B")
    assert swapped == [["B", "A", "C"], ["B", "C", "A"]]

    variants = [["A", "A", "C"]]
    swapped = swap_activities_in_variants(variants, "A", "C")
    assert swapped == [["C", "C", "A"]]

def test_swap_activities():
    # Create a matrix with A -> B dependency
    matrix = AdjacencyMatrix(activities=["A", "B", "C"])
    matrix.add_dependency(
        "A", "B",
        TemporalDependency(TemporalType.DIRECT),
        ExistentialDependency(ExistentialType.IMPLICATION)
    )

    new_matrix = swap_activities(matrix, "A", "C")

    swapped_dep = new_matrix.get_dependency("C", "B")
    assert swapped_dep is not None
    assert swapped_dep[0] is not None
    assert swapped_dep[0].type == TemporalType.DIRECT
    assert swapped_dep[1] is not None
    assert swapped_dep[1].type == ExistentialType.IMPLICATION

    original_dep = new_matrix.get_dependency("A", "B")
    assert original_dep is None or original_dep[0].type == TemporalType.INDEPENDENCE

def test_swap_nonexistent_activity():
    matrix = AdjacencyMatrix(activities=["A", "B"])
    with pytest.raises(ValueError) as excinfo:
        swap_activities(matrix, "A", "X")
    assert "One or both activities not found in the matrix" in str(excinfo.value)
