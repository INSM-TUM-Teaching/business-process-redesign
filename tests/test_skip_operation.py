import pytest
from adjacency_matrix import AdjacencyMatrix
from dependencies import (
    TemporalDependency,
    ExistentialDependency,
    TemporalType,
    ExistentialType,
)
from change_operations.skip_operation import skip_activity, skip_activity_in_variants

def test_skip_activity_from_variants():
    # Test basic deletion (keeping duplicates)
    variants = [["A", "B", "C"], ["A", "C", "B"], ["B", "A"]]
    assert skip_activity_in_variants(variants, "B") == [["A", "B", "C"], ["A", "C"], ["A", "C", "B"], ["B", "A"], ["A"]]
    
    # Test when activity doesn't exist in any variant
    variants = [["A", "C"], ["C", "A"]]
    assert skip_activity_in_variants(variants, "B") == [["A", "C"], ["C", "A"]]
    
    # Test with empty variants
    assert skip_activity_in_variants([], "A") == []