import pytest
from adjacency_matrix import AdjacencyMatrix
from dependencies import (
    TemporalDependency,
    ExistentialDependency,
    TemporalType,
    ExistentialType,
)
from change_operations.collapse_operation import collapse_variant_level, collapse_operation, perform_collapse_variant, get_unique_elements_between_collapse_activities


def test_collapse_variant_level(): 
    # test valid case of collapsing, no activities found in between the activities to collapse
    variants = [["A", "B", "C"], ["C", "A", "B"], ["B", "A"], ["B"]]
    assert collapse_variant_level(None, variants, "X", ["A", "B"]) == [["X", "C"], ["C", "X"], ["X"]]
 
    # test valid case of collapsing, activities can be found in between, but are temporally independent 
    # activity c happends in between, but we ensure it is temporally indepent to other activities 
    variants = [["A", "B", "C"], ["A", "C", "B"], ["B", "A"], ["B"]]
    # Create a simple matrix with A->B->C dependencies
    matrix = AdjacencyMatrix(activities=["A", "B", "C"])
    matrix.add_dependency(
        "C", "A",
        TemporalDependency(TemporalType.INDEPENDENCE),
        ExistentialDependency(ExistentialType.IMPLICATION)

    )
    matrix.add_dependency(
        "C", "B",
        TemporalDependency(TemporalType.INDEPENDENCE), 
        ExistentialDependency(ExistentialType.IMPLICATION)

    )
    assert collapse_variant_level(matrix, variants, "X", ["A", "B"]) == [["X", "C"], ["X"]]

def test_collapse_variant_level_error(): 
    # activity c happends in between, but we ensure it is temporally indepent to other activities 
    variants = [["A", "B", "C"], ["A", "C", "B"], ["B", "A"], ["B"]]
    # Create a simple matrix with A->B->C dependencies
    matrix = AdjacencyMatrix(activities=["A", "B", "C"])
    matrix.add_dependency(
        "C", "A",
        TemporalDependency(TemporalType.EVENTUAL),
        ExistentialDependency(ExistentialType.IMPLICATION)

    )
    matrix.add_dependency(
        "C", "B",
        TemporalDependency(TemporalType.INDEPENDENCE), 
        ExistentialDependency(ExistentialType.IMPLICATION)

    )
    with pytest.raises(ValueError, match="Activity C happens between the activities to be collapsed"):
        collapse_variant_level(matrix, variants, "X", ["A", "B"])


def test_get_unique_elements_between_collapse_activities():
    # test if elements in between exist 
    variants = [["A", "B", "C"], ["A", "C", "B"], ["B", "A"], ["B"]]
    assert get_unique_elements_between_collapse_activities(variants, ["A", "C"]) == ["B"]

    # test if elements in between exist 
    variants = [["A", "B", "C", "D", "E"], ["A", "E", "C", "B"], ["B", "A"], ["B"]]
    assert get_unique_elements_between_collapse_activities(variants, ["A", "C"]) == ["B", "E"]

    # test if no elements in between exist 
    variants = [["A", "B", "C"], ["C", "A", "B"], ["B", "A"], ["B"]]
    assert get_unique_elements_between_collapse_activities(variants, ["A", "B"]) == []


def test_perform_collapse_variant():
    # Test basic collapse on variant level, only operation without any checks 
    variants = [["A", "B", "C"], ["A", "C", "B"], ["B", "A"], ["B"]]
    assert perform_collapse_variant(variants, "X", ["B", "C"]) == [["A", "X"], ["X", "A"], ["X"]]
    
    # Test when collapse_activities don't exist in any variant
    variants = [["A", "C"], ["C", "A"], ["B", "D"]]
    assert perform_collapse_variant(variants, "X", ["Y"]) == [["A", "C"], ["C", "A"], ["B", "D"]]
    
    # Test with empty variants
    assert perform_collapse_variant([], "A", ["B"]) == []
