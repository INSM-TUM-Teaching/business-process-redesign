import pytest
from adjacency_matrix import AdjacencyMatrix
from dependencies import (
    TemporalDependency,
    ExistentialDependency,
    TemporalType,
    ExistentialType,
)
from change_operations.condition_update import condition_update, condition_update_in_variants

def test_condition_update_from_variants():
    # Test basic condition update
    variants = [["A", "B", "C"], ["A", "C", "B"], ["B", "A"]]
    assert condition_update_in_variants(variants, "C", "A") == [["A", "B", "C"], ["A", "C", "B"], ["B"]]
    
    # Test when activity doesn't exist in any variant
    variants = [["A", "C"], ["C", "A"]]
    assert condition_update_in_variants(variants, "A", "B") == [["A", "C"], ["C", "A"]]
    
    # Test with empty variants
    assert condition_update_in_variants([], "A", "B") == []