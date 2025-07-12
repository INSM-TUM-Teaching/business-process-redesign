import pytest
from adjacency_matrix import AdjacencyMatrix
from dependencies import (
    TemporalDependency,
    ExistentialDependency,
    TemporalType,
    ExistentialType,
    Direction,
)
from change_operations.delete_operation import (
    delete_activity,
    delete_activity_from_variants,
)


def test_delete_activity_from_variants():
    # Test basic deletion (keeping duplicates)
    variants = [["A", "B", "C"], ["A", "C", "B"], ["B", "A"]]
    assert delete_activity_from_variants(variants, "B") == [
        ["A", "C"],
        ["A", "C"],
        ["A"],
    ]

    # Test when activity doesn't exist in any variant
    variants = [["A", "C"], ["C", "A"]]
    assert delete_activity_from_variants(variants, "B") == [["A", "C"], ["C", "A"]]

    # Test with empty variants
    assert delete_activity_from_variants([], "A") == []

    # Test duplicate removal
    variants = [["A", "B", "C"], ["B", "A", "C"], ["A", "C"]]
    assert delete_activity_from_variants(variants, "B", remove_duplicates=True) == [
        ["A", "C"]
    ]


def test_delete_activity():
    # Create a simple matrix with A->B->C dependencies
    matrix = AdjacencyMatrix(activities=["A", "B", "C"])
    matrix.add_dependency(
        "A",
        "B",
        TemporalDependency(TemporalType.DIRECT, Direction.FORWARD),
        ExistentialDependency(ExistentialType.IMPLICATION, Direction.FORWARD),
    )
    matrix.add_dependency(
        "B",
        "C",
        TemporalDependency(TemporalType.DIRECT, Direction.FORWARD),
        ExistentialDependency(ExistentialType.IMPLICATION, Direction.FORWARD),
    )

    # Delete activity B
    new_matrix = delete_activity(matrix, "B")

    # Check that B is removed from activities
    assert "B" not in new_matrix.activities
    assert set(new_matrix.activities) == {"A", "C"}

    # Check that dependencies involving B are removed
    for (source, target), _ in new_matrix.dependencies.items():
        assert source != "B" and target != "B"


def test_delete_nonexistent_activity():
    matrix = AdjacencyMatrix(activities=["A", "B"])
    with pytest.raises(ValueError) as excinfo:
        delete_activity(matrix, "X")
    assert "Activity X not found in matrix" in str(excinfo.value)
