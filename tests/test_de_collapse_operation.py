import pytest
from adjacency_matrix import AdjacencyMatrix
from dependencies import (
    TemporalDependency,
    ExistentialDependency,
    TemporalType,
    ExistentialType,
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