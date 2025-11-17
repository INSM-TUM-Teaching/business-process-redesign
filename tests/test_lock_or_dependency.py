"""
Test to verify that OR existential dependency locks are properly validated.
This tests the bug where inserting an activity that prevents both activities
in an OR dependency from occurring should be blocked.
"""

import pytest
from adjacency_matrix import AdjacencyMatrix
from variants_to_matrix import variants_to_matrix
from change_operations.insert_operation import insert_operation
from dependencies import ExistentialDependency, ExistentialType, Direction


def test_insert_violates_or_dependency_should_fail():
    """
    Test that inserting an activity that prevents both activities in a locked OR dependency
    from occurring should be blocked.

    Given:
    - Original process with traces containing at least one of 'h' or 'i' in every trace
    - Locked OR dependency between h and i (at least one must occur)

    When:
    - Attempting to insert activity 'c' with NAND to both 'h' and 'i'
    - This would create traces like 'a,c' where neither 'h' nor 'i' occurs

    Then:
    - Operation should fail with a lock violation error
    """
    # Load BPMN traces that always have at least one of h, i, or j
    with open('sample-matrices/bpmn_traces.txt', 'r') as f:
        traces = [line.strip().split(',') for line in f if line.strip()]

    initial_matrix = variants_to_matrix(traces)

    # Verify the OR dependency exists
    h_to_i_dep = initial_matrix.get_dependency('h', 'i')
    assert h_to_i_dep is not None
    _, existential = h_to_i_dep
    assert existential.type == ExistentialType.OR, "h->i should have OR dependency"

    # Verify that all traces have at least one of h or i
    for trace in traces:
        assert 'h' in trace or 'i' in trace, f"All traces should have h or i, but got: {trace}"

    # Define locks - lock the OR dependency between h and i
    locked_dependencies = {
        ('h', 'i'): (False, True),  # Lock existential dependency only
    }

    # Define the insert operation that would violate the OR constraint
    # Insert 'c' with NAND to both h and i (and j)
    new_dependencies = [
        # c can only occur if a occurs
        {
            'from': 'a',
            'to': 'c',
            'temporal': 'DIRECT',
            'existential': 'IMPLICATION',
            'existential_direction': 'BACKWARD'
        },
        # c cannot coexist with h, i, j, or the other activities
        {'from': 'b', 'to': 'c', 'temporal': 'INDEPENDENCE', 'existential': 'NAND'},
        {'from': 'd', 'to': 'c', 'temporal': 'INDEPENDENCE', 'existential': 'NAND'},
        {'from': 'e', 'to': 'c', 'temporal': 'INDEPENDENCE', 'existential': 'NAND'},
        {'from': 'f', 'to': 'c', 'temporal': 'INDEPENDENCE', 'existential': 'NAND'},
        {'from': 'g', 'to': 'c', 'temporal': 'INDEPENDENCE', 'existential': 'NAND'},
        {'from': 'h', 'to': 'c', 'temporal': 'INDEPENDENCE', 'existential': 'NAND'},
        {'from': 'i', 'to': 'c', 'temporal': 'INDEPENDENCE', 'existential': 'NAND'},
        {'from': 'j', 'to': 'c', 'temporal': 'INDEPENDENCE', 'existential': 'NAND'},
    ]

    # This should raise a ValueError because it violates the locked OR dependency
    with pytest.raises(ValueError, match=".*lock.*violated.*|.*OR.*constraint.*"):
        modified_matrix = insert_operation(
            initial_matrix,
            'c',
            new_dependencies,
            locked_dependencies
        )
