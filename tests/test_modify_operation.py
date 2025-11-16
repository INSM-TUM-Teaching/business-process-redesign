import pytest
from adjacency_matrix import AdjacencyMatrix
from dependencies import (
    TemporalDependency,
    ExistentialDependency,
    TemporalType,
    ExistentialType,
    Direction,
)
from change_operations.modify_operation import modify_dependencies


def test_modify_single_consequence_possible():
    """
    Test Case 1: Single consequence with possible implementation

    Input Matrix:
        a    b         c          d
    a   x  (<d,<=)   (<d,<=)   (<,<=>)
    b       x     (-, NAND)   (<d, =>)
    c              x        (<d, =>)
    d                        x

    Operation: Modify (a,d) = (<,<=)
    Note: only existential dependency is modified from <=> to <=

    Expected: Only (a,d) should change
    """
    # Create input matrix
    matrix = AdjacencyMatrix(activities=["a", "b", "c", "d"])

    # Row a: (<d,<=) means temporal=<d (DIRECT/FORWARD), existential=<= (IMPLICATION/BACKWARD)
    matrix.add_dependency(
        "a", "b",
        TemporalDependency(TemporalType.DIRECT, direction=Direction.FORWARD),
        ExistentialDependency(ExistentialType.IMPLICATION, direction=Direction.BACKWARD)
    )
    matrix.add_dependency(
        "a", "c",
        TemporalDependency(TemporalType.DIRECT, direction=Direction.FORWARD),
        ExistentialDependency(ExistentialType.IMPLICATION, direction=Direction.BACKWARD)
    )
    matrix.add_dependency(
        "a", "d",
        TemporalDependency(TemporalType.EVENTUAL, direction=Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, direction=Direction.BOTH)
    )

    # Row b
    matrix.add_dependency(
        "b", "a",
        TemporalDependency(TemporalType.DIRECT, direction=Direction.BACKWARD),
        ExistentialDependency(ExistentialType.IMPLICATION, direction=Direction.FORWARD)
    )
    matrix.add_dependency(
        "b", "c",
        TemporalDependency(TemporalType.INDEPENDENCE, direction=Direction.BOTH),
        ExistentialDependency(ExistentialType.NAND, direction=Direction.BOTH)
    )
    matrix.add_dependency(
        "b", "d",
        TemporalDependency(TemporalType.DIRECT, direction=Direction.FORWARD),
        ExistentialDependency(ExistentialType.IMPLICATION, direction=Direction.FORWARD)
    )

    # Row c
    matrix.add_dependency(
        "c", "a",
        TemporalDependency(TemporalType.DIRECT, direction=Direction.BACKWARD),
        ExistentialDependency(ExistentialType.IMPLICATION, direction=Direction.FORWARD)
    )
    matrix.add_dependency(
        "c", "b",
        TemporalDependency(TemporalType.INDEPENDENCE, direction=Direction.BOTH),
        ExistentialDependency(ExistentialType.NAND, direction=Direction.BOTH)
    )
    matrix.add_dependency(
        "c", "d",
        TemporalDependency(TemporalType.DIRECT, direction=Direction.FORWARD),
        ExistentialDependency(ExistentialType.IMPLICATION, direction=Direction.FORWARD)
    )

    # Row d
    matrix.add_dependency(
        "d", "a",
        TemporalDependency(TemporalType.EVENTUAL, direction=Direction.BACKWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, direction=Direction.BOTH)
    )
    matrix.add_dependency(
        "d", "b",
        TemporalDependency(TemporalType.DIRECT, direction=Direction.BACKWARD),
        ExistentialDependency(ExistentialType.IMPLICATION, direction=Direction.BACKWARD)
    )
    matrix.add_dependency(
        "d", "c",
        TemporalDependency(TemporalType.DIRECT, direction=Direction.BACKWARD),
        ExistentialDependency(ExistentialType.IMPLICATION, direction=Direction.BACKWARD)
    )

    # Create modification: (a,d) = (<,<=)
    modifications = [
        ("a", "d",
         TemporalDependency(TemporalType.EVENTUAL, direction=Direction.FORWARD),
         ExistentialDependency(ExistentialType.IMPLICATION, direction=Direction.FORWARD))
    ]

    # Apply modification
    result_matrix, changed_cells = modify_dependencies(matrix, modifications)

    # Verify only (a,d) and (d,a) changed (bidirectional dependency = 2 cells)
    assert len(changed_cells) == 2, f"Expected 2 changed cells (a,d) and (d,a), got {len(changed_cells)}: {changed_cells}"
    assert ("a", "d") in changed_cells, f"Expected ('a', 'd') in changed cells, got {changed_cells}"
    assert ("d", "a") in changed_cells, f"Expected ('d', 'a') in changed cells, got {changed_cells}"


def test_modify_two_consequences_possible():
    """
    Test Case 2: 4 changes (2 pairs) with cascading consequence

    Input Matrix:
        a    b         c          d
    a   x  (<d,<=)   (<d,<=)   (<,<=>)
    b       x     (-,<=/=>)   (<d, =>)
    c              x        (<d,=>)
    d                        x

    Operation: Modify (c,d) = (-, V)

    Expected: 4 changes at (a,c), (c,a), (c,d), (d,c)
    The modification creates new sequence ['a', 'd', 'c'], causing (a,c) to change from DIRECT to EVENTUAL
    """
    # Create input matrix
    matrix = AdjacencyMatrix(activities=["a", "b", "c", "d"])

    # Row a: (<d,<=) means temporal=<d (DIRECT/FORWARD), existential=<= (IMPLICATION/BACKWARD)
    matrix.add_dependency(
        "a", "b",
        TemporalDependency(TemporalType.DIRECT, direction=Direction.FORWARD),
        ExistentialDependency(ExistentialType.IMPLICATION, direction=Direction.BACKWARD)
    )
    matrix.add_dependency(
        "a", "c",
        TemporalDependency(TemporalType.DIRECT, direction=Direction.FORWARD),
        ExistentialDependency(ExistentialType.IMPLICATION, direction=Direction.BACKWARD)
    )
    matrix.add_dependency(
        "a", "d",
        TemporalDependency(TemporalType.EVENTUAL, direction=Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, direction=Direction.BOTH)
    )

    # Row b
    matrix.add_dependency(
        "b", "a",
        TemporalDependency(TemporalType.DIRECT, direction=Direction.BACKWARD),
        ExistentialDependency(ExistentialType.IMPLICATION, direction=Direction.FORWARD)
    )
    matrix.add_dependency(
        "b", "c",
        TemporalDependency(TemporalType.INDEPENDENCE, direction=Direction.BOTH),
        ExistentialDependency(ExistentialType.NEGATED_EQUIVALENCE, direction=Direction.BOTH)
    )
    matrix.add_dependency(
        "b", "d",
        TemporalDependency(TemporalType.DIRECT, direction=Direction.FORWARD),
        ExistentialDependency(ExistentialType.IMPLICATION, direction=Direction.FORWARD)
    )

    # Row c
    matrix.add_dependency(
        "c", "a",
        TemporalDependency(TemporalType.DIRECT, direction=Direction.BACKWARD),
        ExistentialDependency(ExistentialType.IMPLICATION, direction=Direction.FORWARD)
    )
    matrix.add_dependency(
        "c", "b",
        TemporalDependency(TemporalType.INDEPENDENCE, direction=Direction.BOTH),
        ExistentialDependency(ExistentialType.NEGATED_EQUIVALENCE, direction=Direction.BOTH)
    )
    matrix.add_dependency(
        "c", "d",
        TemporalDependency(TemporalType.DIRECT, direction=Direction.FORWARD),
        ExistentialDependency(ExistentialType.IMPLICATION, direction=Direction.FORWARD)
    )

    # Row d
    matrix.add_dependency(
        "d", "a",
        TemporalDependency(TemporalType.EVENTUAL, direction=Direction.BACKWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, direction=Direction.BOTH)
    )
    matrix.add_dependency(
        "d", "b",
        TemporalDependency(TemporalType.DIRECT, direction=Direction.BACKWARD),
        ExistentialDependency(ExistentialType.IMPLICATION, direction=Direction.BACKWARD)
    )
    matrix.add_dependency(
        "d", "c",
        TemporalDependency(TemporalType.DIRECT, direction=Direction.BACKWARD),
        ExistentialDependency(ExistentialType.IMPLICATION, direction=Direction.BACKWARD)
    )

    # Create modification: (c,d) = (-, V)
    modifications = [
        ("c", "d",
         TemporalDependency(TemporalType.INDEPENDENCE, direction=Direction.BOTH),
         ExistentialDependency(ExistentialType.OR, direction=Direction.BOTH))
    ]

    # Apply modification
    result_matrix, changed_cells = modify_dependencies(matrix, modifications)

    # Verify 4 changes: (c,d), (d,c), (a,c), (c,a)
    # The modification creates a new sequence ['a', 'd', 'c'] which makes (a,c) change from DIRECT to EVENTUAL
    assert len(changed_cells) == 4, f"Expected 4 changed cells, got {len(changed_cells)}: {changed_cells}"
    assert ("c", "d") in changed_cells, f"Expected ('c', 'd') in changed cells, got {changed_cells}"
    assert ("d", "c") in changed_cells, f"Expected ('d', 'c') in changed cells, got {changed_cells}"
    assert ("a", "c") in changed_cells, f"Expected ('a', 'c') in changed cells, got {changed_cells}"
    assert ("c", "a") in changed_cells, f"Expected ('c', 'a') in changed cells, got {changed_cells}"


def test_modify_contradiction_requires_more():
    """
    Test Case 3: Testcase that does not work and requires further modification tuples

    Input Matrix:
        a    b         c          d
    a   x  (<d,<=>)  (<,<=>)   (<,<=>)
    b       x     (<d,<=>)   (<,<=>)
    c              x      (<d,<=>)
    d                      x

    Operation: Modify (b,c) = (-,<=/=>)

    Expected: ValueError with contradiction message
    """
    # Create input matrix
    matrix = AdjacencyMatrix(activities=["a", "b", "c", "d"])

    # Row a
    matrix.add_dependency(
        "a", "b",
        TemporalDependency(TemporalType.DIRECT, direction=Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, direction=Direction.BOTH)
    )
    matrix.add_dependency(
        "a", "c",
        TemporalDependency(TemporalType.EVENTUAL, direction=Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, direction=Direction.BOTH)
    )
    matrix.add_dependency(
        "a", "d",
        TemporalDependency(TemporalType.EVENTUAL, direction=Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, direction=Direction.BOTH)
    )

    # Row b
    matrix.add_dependency(
        "b", "a",
        TemporalDependency(TemporalType.DIRECT, direction=Direction.BACKWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, direction=Direction.BOTH)
    )
    matrix.add_dependency(
        "b", "c",
        TemporalDependency(TemporalType.DIRECT, direction=Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, direction=Direction.BOTH)
    )
    matrix.add_dependency(
        "b", "d",
        TemporalDependency(TemporalType.EVENTUAL, direction=Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, direction=Direction.BOTH)
    )

    # Row c
    matrix.add_dependency(
        "c", "a",
        TemporalDependency(TemporalType.EVENTUAL, direction=Direction.BACKWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, direction=Direction.BOTH)
    )
    matrix.add_dependency(
        "c", "b",
        TemporalDependency(TemporalType.DIRECT, direction=Direction.BACKWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, direction=Direction.BOTH)
    )
    matrix.add_dependency(
        "c", "d",
        TemporalDependency(TemporalType.DIRECT, direction=Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, direction=Direction.BOTH)
    )

    # Row d
    matrix.add_dependency(
        "d", "a",
        TemporalDependency(TemporalType.EVENTUAL, direction=Direction.BACKWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, direction=Direction.BOTH)
    )
    matrix.add_dependency(
        "d", "b",
        TemporalDependency(TemporalType.EVENTUAL, direction=Direction.BACKWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, direction=Direction.BOTH)
    )
    matrix.add_dependency(
        "d", "c",
        TemporalDependency(TemporalType.DIRECT, direction=Direction.BACKWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, direction=Direction.BOTH)
    )

    # Create modification: (b,c) = (-,<=/=>)
    modifications = [
        ("b", "c",
         TemporalDependency(TemporalType.INDEPENDENCE, direction=Direction.BOTH),
         ExistentialDependency(ExistentialType.NEGATED_EQUIVALENCE, direction=Direction.BOTH))
    ]

    # Apply modification - should raise ValueError
    with pytest.raises(ValueError) as exc_info:
        modify_dependencies(matrix, modifications)

    # Verify error message contains contradiction information
    error_msg = str(exc_info.value)
    assert "Contradictions detected" in error_msg
    assert "modification cannot be implemented" in error_msg


def test_modify_four_consequences_possible():
    """
    Test Case 4: Testcase with cascading consequences + possible implementation

    Input Matrix:
        a    b         c          d
    a   x  (<d,<=)   (<d,<=)   (<,<=>)
    b       x     (-, NAND)   (<d, =>)
    c              x        (<d,=>)
    d                        x

    Operation: Modify (b,c) = (<d, <=>)

    Expected: 6 changes (3 pairs with forward and reverse)
    Changes:
    - (a,c) and (c,a): temporal <d -> <
    - (b,c) and (c,b): both temporal and existential (-, NAND) -> (<d, <=>)
    - (b,d) and (d,b): temporal <d -> <
    Note: (c,d) stays DIRECT because c and d remain adjacent in acceptance sequences
    """
    # Create input matrix
    matrix = AdjacencyMatrix(activities=["a", "b", "c", "d"])

    # Row a: (<d,<=) means temporal=<d (DIRECT/FORWARD), existential=<= (IMPLICATION/BACKWARD)
    matrix.add_dependency(
        "a", "b",
        TemporalDependency(TemporalType.DIRECT, direction=Direction.FORWARD),
        ExistentialDependency(ExistentialType.IMPLICATION, direction=Direction.BACKWARD)
    )
    matrix.add_dependency(
        "a", "c",
        TemporalDependency(TemporalType.DIRECT, direction=Direction.FORWARD),
        ExistentialDependency(ExistentialType.IMPLICATION, direction=Direction.BACKWARD)
    )
    matrix.add_dependency(
        "a", "d",
        TemporalDependency(TemporalType.EVENTUAL, direction=Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, direction=Direction.BOTH)
    )

    # Row b
    matrix.add_dependency(
        "b", "a",
        TemporalDependency(TemporalType.DIRECT, direction=Direction.BACKWARD),
        ExistentialDependency(ExistentialType.IMPLICATION, direction=Direction.FORWARD)
    )
    matrix.add_dependency(
        "b", "c",
        TemporalDependency(TemporalType.INDEPENDENCE, direction=Direction.BOTH),
        ExistentialDependency(ExistentialType.NAND, direction=Direction.BOTH)
    )
    matrix.add_dependency(
        "b", "d",
        TemporalDependency(TemporalType.DIRECT, direction=Direction.FORWARD),
        ExistentialDependency(ExistentialType.IMPLICATION, direction=Direction.FORWARD)
    )

    # Row c
    matrix.add_dependency(
        "c", "a",
        TemporalDependency(TemporalType.DIRECT, direction=Direction.BACKWARD),
        ExistentialDependency(ExistentialType.IMPLICATION, direction=Direction.FORWARD)
    )
    matrix.add_dependency(
        "c", "b",
        TemporalDependency(TemporalType.INDEPENDENCE, direction=Direction.BOTH),
        ExistentialDependency(ExistentialType.NAND, direction=Direction.BOTH)
    )
    matrix.add_dependency(
        "c", "d",
        TemporalDependency(TemporalType.DIRECT, direction=Direction.FORWARD),
        ExistentialDependency(ExistentialType.IMPLICATION, direction=Direction.FORWARD)
    )

    # Row d
    matrix.add_dependency(
        "d", "a",
        TemporalDependency(TemporalType.EVENTUAL, direction=Direction.BACKWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, direction=Direction.BOTH)
    )
    matrix.add_dependency(
        "d", "b",
        TemporalDependency(TemporalType.DIRECT, direction=Direction.BACKWARD),
        ExistentialDependency(ExistentialType.IMPLICATION, direction=Direction.BACKWARD)
    )
    matrix.add_dependency(
        "d", "c",
        TemporalDependency(TemporalType.DIRECT, direction=Direction.BACKWARD),
        ExistentialDependency(ExistentialType.IMPLICATION, direction=Direction.BACKWARD)
    )

    # Create modification: (b,c) = (<d, <=>)
    modifications = [
        ("b", "c",
         TemporalDependency(TemporalType.DIRECT, direction=Direction.FORWARD),
         ExistentialDependency(ExistentialType.EQUIVALENCE, direction=Direction.BOTH))
    ]

    # Apply modification
    result_matrix, changed_cells = modify_dependencies(matrix, modifications)

    # Verify 6 changes (3 pairs with both forward and reverse directions):
    # - (a,c) and (c,a) - temporal change from DIRECT to EVENTUAL
    # - (b,c) and (c,b) - both temporal and existential change
    # - (b,d) and (d,b) - temporal change from DIRECT to EVENTUAL
    # Note: (c,d) does NOT change because it stays DIRECT in rediscovered matrix
    assert len(changed_cells) == 6, f"Expected 6 changed cells, got {len(changed_cells)}: {changed_cells}"

    # Check that the expected pairs are in the changed list (both forward and reverse)
    expected_pairs = [("a", "c"), ("b", "c"), ("b", "d")]
    for pair in expected_pairs:
        forward = pair in changed_cells
        reverse = (pair[1], pair[0]) in changed_cells
        assert forward and reverse, f"Expected both {pair} and its reverse in changed cells, got {changed_cells}"


def test_modify_invalid_activity():
    """
    Test error handling when modification references non-existent activity
    """
    matrix = AdjacencyMatrix(activities=["a", "b", "c"])

    matrix.add_dependency(
        "a", "b",
        TemporalDependency(TemporalType.DIRECT, direction=Direction.FORWARD),
        ExistentialDependency(ExistentialType.IMPLICATION, direction=Direction.FORWARD)
    )

    # Try to modify with invalid activity
    modifications = [
        ("a", "z",  # 'z' doesn't exist
         TemporalDependency(TemporalType.EVENTUAL, direction=Direction.FORWARD),
         ExistentialDependency(ExistentialType.IMPLICATION, direction=Direction.FORWARD))
    ]

    with pytest.raises(ValueError) as exc_info:
        modify_dependencies(matrix, modifications)

    assert "not found in matrix" in str(exc_info.value)


def test_modify_empty_modifications():
    """
    Test error handling when modifications list is empty
    """
    matrix = AdjacencyMatrix(activities=["a", "b", "c"])

    matrix.add_dependency(
        "a", "b",
        TemporalDependency(TemporalType.DIRECT, direction=Direction.FORWARD),
        ExistentialDependency(ExistentialType.IMPLICATION, direction=Direction.FORWARD)
    )

    # Try to modify with empty list
    modifications = []

    with pytest.raises(ValueError) as exc_info:
        modify_dependencies(matrix, modifications)

    assert "cannot be empty" in str(exc_info.value)
