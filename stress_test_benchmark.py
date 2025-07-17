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


def create_complex_test_matrix(size=6, complexity=0.5) -> AdjacencyMatrix:
    """
    Create a more complex test matrix with many interdependencies.
    
    Args:
        size: Number of activities
        complexity: Between 0 and 1, determines how many dependencies to add
    """
    activities = [chr(65 + i) for i in range(min(size, 26))]
    if size > 26:
        activities.extend([f"A{i}" for i in range(size - 26)])
    
    matrix = AdjacencyMatrix(activities=activities)
    
    for i in range(size - 1):
        matrix.add_dependency(
            activities[i],
            activities[i+1],
            TemporalDependency(TemporalType.DIRECT, Direction.FORWARD),
            None
        )
    
    # Add existential dependencies based on complexity
    max_deps = int((size * (size - 1) / 2) * complexity)
    deps_added = 0
    
    all_pairs = [(i, j) for i in range(size) for j in range(size) if i != j]
    random.shuffle(all_pairs)
    
    existential_types = [
        ExistentialType.IMPLICATION,
        ExistentialType.EQUIVALENCE,
        ExistentialType.OR,
        ExistentialType.NAND
    ]
    
    for i, j in all_pairs:
        if deps_added >= max_deps:
            break
            
        # Skip if we already have a dependency for this pair
        if matrix.get_dependency(activities[i], activities[j]) is not None:
            continue
            
        e_type = random.choice(existential_types)
        direction = Direction.FORWARD if random.random() < 0.7 else Direction.BOTH
        
        matrix.add_dependency(
            activities[i],
            activities[j],
            None,
            ExistentialDependency(e_type, direction)
        )
        
        deps_added += 1
    
    return matrix


def run_stress_test_benchmark():
    """
    Run a more stressful benchmark with more complex matrices.
    """
    print("Running stress test benchmark...")
    
    test_cases = [
        {"size": 7, "complexity": 0.3},
        {"size": 8, "complexity": 0.3},
        {"size": 9, "complexity": 0.3},
        {"size": 10, "complexity": 0.25},
        {"size": 12, "complexity": 0.2},
        {"size": 14, "complexity": 0.15},
        {"size": 16, "complexity": 0.1},
        {"size": 18, "complexity": 0.1},
        {"size": 20, "complexity": 0.05}
    ]
    
    print("\nSize | Complexity | Original Time | Optimized Time | Speedup | Original Count | Optimized Count")
    print("-" * 90)
    
    for case in test_cases:
        size = case["size"]
        complexity = case["complexity"]
        
        matrix = create_complex_test_matrix(size, complexity)
        
        # Time the original implementation for smaller sizes
        if size <= 8:
            start_time = time.time()
            try:
                original_result = generate_acceptance_variants(matrix)
                original_time = time.time() - start_time
                original_count = len(original_result)
            except Exception as e:
                print(f"Original implementation failed for size {size}: {str(e)}")
                original_time = float('inf')
                original_count = "Error"
        else:
            original_time = float('inf')
            original_count = "Skipped"
        
        # Time the optimized implementation
        start_time = time.time()
        try:
            optimized_result = generate_optimized_acceptance_variants(matrix)
            optimized_time = time.time() - start_time
            optimized_count = len(optimized_result)
        except Exception as e:
            print(f"Optimized implementation failed for size {size}: {str(e)}")
            optimized_time = float('inf')
            optimized_count = "Error"
        
        # Calculate speedup if possible
        if original_time != float('inf') and optimized_time != float('inf') and optimized_time > 0:
            speedup = original_time / optimized_time
            speedup_str = f"{speedup:.2f}x"
        else:
            speedup_str = "N/A"
        
        # Format times
        orig_time_str = f"{original_time:.4f}s" if original_time != float('inf') else "Skipped"
        opt_time_str = f"{optimized_time:.4f}s" if optimized_time != float('inf') else "Failed"
        
        orig_count_str = str(original_count)
        opt_count_str = str(optimized_count)
        
        print(f"{size:4d} | {complexity:.2f}      | {orig_time_str:13s} | {opt_time_str:14s} | {speedup_str:7s} | {orig_count_str:14s} | {opt_count_str}")


if __name__ == "__main__":
    # Set random seed for reproducibility
    random.seed(42)
    run_stress_test_benchmark()
