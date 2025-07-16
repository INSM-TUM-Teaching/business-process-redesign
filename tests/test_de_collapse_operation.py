import pytest
from adjacency_matrix import AdjacencyMatrix
from dependencies import (
    TemporalDependency,
    ExistentialDependency,
    TemporalType,
    ExistentialType,
    Direction
)
from change_operations.de_collapse_operation import decollapse_operation, decollapse_variant_level

def test_de_collapse_from_variants():
    # Test basic condition update
    variants = [["A", "B", "C"], ["A", "C", "B"], ["B", "A"]]
    variants_to_decollapse = [["X", "Y"], ["Y", "X"]]

    assert decollapse_variant_level(variants, "A", variants_to_decollapse) == [["X", "Y", "B", "C"], ["Y", "X", "B", "C"], ["X", "Y", "C", "B"], ["Y", "X", "C", "B"], ["B", "X", "Y"], ["B", "Y", "X"]]
    
    # Test when activity doesn't exist in any variant
    variants = [["A", "C"], ["C", "A"]]
    assert decollapse_variant_level(variants, "B", variants_to_decollapse) == [["A", "C"], ["C", "A"]]
    
    # Test with empty variants
    assert decollapse_variant_level([], "A", variants_to_decollapse) == []

def test_de_collapse_activity_double():  

    # Create a simple matrix with A < B < C dependencies
    matrix = AdjacencyMatrix(activities=["A", "B", "C"])

    # create the collapsed matrix which we use for test
    collapsed_matrix = AdjacencyMatrix(activities=["A", "B"])

    # perform the test that for de-collapsing an error will occur, since the activity is contained double 
    with pytest.raises(ValueError, match="Activity B is in matrix and collapsed matrix, activities would be defined ambigously after collapsing"):
        decollapse_operation(matrix, "A", collapsed_matrix)
