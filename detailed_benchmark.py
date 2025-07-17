import time
import random
from typing import List, Tuple
import sys

from adjacency_matrix import AdjacencyMatrix
from dependencies import (
    TemporalType,
    ExistentialType,
    TemporalDependency,
    ExistentialDependency,
    Direction,
)
from acceptance_variants import generate_acceptance_variants
from optimized_acceptance_variants import generate_optimized_acceptance_variants


def create_test_matrix(size=6) -> AdjacencyMatrix:
    """
    Create a standard test matrix with more complex dependencies.
    """
    activities = [chr(65 + i) for i in range(min(size, 26))]
    if size > 26:
        activities.extend([f"A{i}" for i in range(size - 26)])
    
    matrix = AdjacencyMatrix(activities=activities)
    
    # Add a mix of temporal and existential dependencies
    for i in range(size - 1):
        matrix.add_dependency(
            activities[i],
            activities[i+1],
            TemporalDependency(TemporalType.DIRECT, Direction.FORWARD),
            ExistentialDependency(ExistentialType.IMPLICATION, Direction.FORWARD)
        )
        
        if i < size - 2:
            matrix.add_dependency(
                activities[i],
                activities[i+2],
                TemporalDependency(TemporalType.EVENTUAL, Direction.FORWARD),
                ExistentialDependency(ExistentialType.OR, Direction.BOTH)
            )
    
    matrix.add_dependency(
        activities[-1],
        activities[0],
        TemporalDependency(TemporalType.INDEPENDENCE, Direction.BOTH),
        ExistentialDependency(ExistentialType.NAND, Direction.BOTH)
    )
    
    if size > 3:
        matrix.add_dependency(
            activities[-1],
            activities[2],
            TemporalDependency(TemporalType.INDEPENDENCE, Direction.BOTH),
            ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
        )
    
    return matrix


def run_detailed_benchmark():
    """
    Run a more controlled benchmark to better demonstrate the performance difference.
    """
    print("Running detailed acceptance variants benchmark...")
    
    # Test matrices of increasing complexity
    sizes = [5, 6, 7, 8, 9, 10]
    
    for size in sizes:
        matrix = create_test_matrix(size)
        
        print(f"\nTesting matrix with {size} activities:")
        
        # Time the original implementation
        if size <= 7:
            start_time = time.time()
            try:
                original_result = generate_acceptance_variants(matrix)
                original_time = time.time() - start_time
                print(f"Original implementation: {original_time:.4f} seconds, {len(original_result)} variants")
            except Exception as e:
                print(f"Original implementation failed: {str(e)}")
                original_result = []
                original_time = float('inf')
        else:
            print("Original implementation: Skipped for size > 7")
            original_result = []
            original_time = float('inf')
        
        # Time the optimized implementation
        start_time = time.time()
        try:
            optimized_result = generate_optimized_acceptance_variants(matrix)
            optimized_time = time.time() - start_time
            print(f"Optimized implementation: {optimized_time:.4f} seconds, {len(optimized_result)} variants")
            
            # Check if results match for smaller sizes
            if size <= 7 and len(original_result) > 0:
                orig_sorted = sorted([tuple(v) for v in original_result])
                opt_sorted = sorted([tuple(v) for v in optimized_result])
                if orig_sorted != opt_sorted:
                    print(f"WARNING: Results do not match for size {size}")
                    
                    # Print first few differences for debugging
                    if len(orig_sorted) != len(opt_sorted):
                        print(f"  Original has {len(orig_sorted)} variants, Optimized has {len(opt_sorted)}")
                    
                    # Find which variants are in one but not the other
                    if len(orig_sorted) < 10 and len(opt_sorted) < 10:
                        orig_set = set(orig_sorted)
                        opt_set = set(opt_sorted)
                        only_in_orig = orig_set - opt_set
                        only_in_opt = opt_set - orig_set
                        
                        if only_in_orig:
                            print("  Only in original:", only_in_orig)
                        if only_in_opt:
                            print("  Only in optimized:", only_in_opt)
                else:
                    print("  Results match!")
        except Exception as e:
            print(f"Optimized implementation failed: {str(e)}")
            optimized_time = float('inf')
        
        # Calculate speedup if possible
        if original_time != float('inf') and optimized_time != float('inf') and optimized_time > 0:
            speedup = original_time / optimized_time
            print(f"Speedup: {speedup:.2f}x")
        else:
            print("Speedup: N/A")


if __name__ == "__main__":
    run_detailed_benchmark()
