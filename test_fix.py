#!/usr/bin/env python3
"""
Simple test script to verify the OR dependency lock fix works correctly.
This script tests that inserting activity 'c' with NAND to h and i is blocked
when there's a locked OR dependency between h and i.
"""

import sys
from variants_to_matrix import variants_to_matrix
from change_operations.insert_operation import insert_operation
from dependencies import ExistentialType

def test_or_dependency_violation():
    print("=" * 80)
    print("Testing OR Dependency Lock Violation Detection")
    print("=" * 80)

    # Load BPMN traces
    print("\n1. Loading BPMN traces...")
    with open('sample-matrices/bpmn_traces.txt', 'r') as f:
        traces = [line.strip().split(',') for line in f if line.strip()]
    print(f"   Loaded {len(traces)} traces")

    # Create initial matrix
    print("\n2. Creating initial matrix...")
    initial_matrix = variants_to_matrix(traces)
    activities = initial_matrix.get_activities()
    print(f"   Activities: {sorted(activities)}")

    # Verify the OR dependency exists
    print("\n3. Checking h->i dependency...")
    h_to_i_dep = initial_matrix.get_dependency('h', 'i')
    if h_to_i_dep:
        _, existential = h_to_i_dep
        print(f"   Existential dependency: {existential.type}")
        if existential.type == ExistentialType.OR:
            print("   ✓ Confirmed: h->i has OR dependency (at least one must occur)")
        else:
            print(f"   ✗ Unexpected dependency type: {existential.type}")
            return False
    else:
        print("   ✗ No dependency found between h and i")
        return False

    # Verify all original traces have at least one of h or i
    print("\n4. Verifying OR constraint in original traces...")
    traces_without_h_or_i = [t for t in traces if 'h' not in t and 'i' not in t]
    print(f"   Traces without h or i: {len(traces_without_h_or_i)} out of {len(traces)}")
    if traces_without_h_or_i:
        print(f"   ✗ Some original traces violate OR constraint: {traces_without_h_or_i[:3]}")
        return False
    else:
        print("   ✓ All original traces satisfy OR constraint")

    # Define locks - lock the OR dependency between h and i
    print("\n5. Setting up locked dependencies...")
    locked_dependencies = {
        ('h', 'i'): (False, True),  # Lock existential dependency
    }
    print("   Locked: h->i (existential)")

    # Define the insert operation that would violate the OR constraint
    print("\n6. Attempting to insert 'c' with NAND to h, i, j...")
    new_dependencies = [
        {'from': 'a', 'to': 'c', 'temporal': 'DIRECT', 'existential': 'IMPLICATION', 'existential_direction': 'BACKWARD'},
        {'from': 'b', 'to': 'c', 'temporal': 'INDEPENDENCE', 'existential': 'NAND'},
        {'from': 'd', 'to': 'c', 'temporal': 'INDEPENDENCE', 'existential': 'NAND'},
        {'from': 'h', 'to': 'c', 'temporal': 'INDEPENDENCE', 'existential': 'NAND'},
        {'from': 'i', 'to': 'c', 'temporal': 'INDEPENDENCE', 'existential': 'NAND'},
        {'from': 'j', 'to': 'c', 'temporal': 'INDEPENDENCE', 'existential': 'NAND'},
    ]
    print("   Dependencies: c can only occur with a, not with h, i, or j (NAND)")

    # Try to insert - this should fail with the fix
    print("\n7. Running insert operation...")
    try:
        modified_matrix = insert_operation(initial_matrix, 'c', new_dependencies, locked_dependencies)
        print("   ✗ BUG: Insert operation succeeded when it should have failed!")
        print("   The OR constraint between h and i would be violated.")

        # Show the violation
        from optimized_acceptance_variants import generate_optimized_acceptance_variants
        new_traces = generate_optimized_acceptance_variants(modified_matrix)
        traces_without_h_or_i_after = [t for t in new_traces if 'h' not in t and 'i' not in t]
        print(f"\n   Violating traces (neither h nor i): {len(traces_without_h_or_i_after)}")
        if traces_without_h_or_i_after:
            print(f"   Example: {traces_without_h_or_i_after[0]}")

        return False

    except ValueError as e:
        print(f"   ✓ EXPECTED: Insert operation correctly blocked!")
        print(f"   Error message: {str(e)}")
        return True

if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("OR Dependency Lock Violation Test")
    print("=" * 80)

    try:
        success = test_or_dependency_violation()

        print("\n" + "=" * 80)
        if success:
            print("✓ TEST PASSED: OR dependency lock is properly enforced")
            print("=" * 80)
            sys.exit(0)
        else:
            print("✗ TEST FAILED: OR dependency lock is not enforced")
            print("=" * 80)
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
