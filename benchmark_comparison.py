import time
import random
from typing import List, Tuple

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


def generate_random_matrix(n_activities: int, dependency_density: float = 0.3) -> AdjacencyMatrix:
    """
    Generate a random adjacency matrix with the given number of activities and dependency density.
    
    Args:
        n_activities: Number of activities in the matrix
        dependency_density: Probability of having a dependency between any two activities
        
    Returns:
        A randomly generated AdjacencyMatrix
    """
    activities = [chr(65 + i) for i in range(min(n_activities, 26))]
    if n_activities > 26:
        activities.extend([f"A{i}" for i in range(n_activities - 26)])
    
    matrix = AdjacencyMatrix(activities=activities)
    
    temporal_types = [
        TemporalType.DIRECT,
        TemporalType.EVENTUAL,
        TemporalType.INDEPENDENCE
    ]
    
    existential_types = [
        ExistentialType.IMPLICATION,
        ExistentialType.EQUIVALENCE,
        ExistentialType.NEGATED_EQUIVALENCE,
        ExistentialType.NAND,
        ExistentialType.OR,
        ExistentialType.INDEPENDENCE
    ]
    
    directions = [Direction.FORWARD, Direction.BACKWARD, Direction.BOTH]
    
    for i in range(n_activities):
        for j in range(n_activities):
            if i != j and random.random() < dependency_density:
                temporal_type = random.choice(temporal_types)
                existential_type = random.choice(existential_types)
                
                temporal_direction = Direction.BOTH
                if temporal_type in [TemporalType.DIRECT, TemporalType.EVENTUAL]:
                    temporal_direction = random.choice(directions)
                    
                existential_direction = Direction.BOTH
                if existential_type == ExistentialType.IMPLICATION:
                    existential_direction = random.choice(directions)
                
                temporal_dep = TemporalDependency(type=temporal_type, direction=temporal_direction)
                existential_dep = ExistentialDependency(type=existential_type, direction=existential_direction)
                
                matrix.add_dependency(
                    activities[i], 
                    activities[j], 
                    temporal_dep, 
                    existential_dep
                )
    
    return matrix


def benchmark_comparison(max_activities: int = 8, trials_per_size: int = 2, timeout_sec: int = 60) -> Tuple[List[int], List[float], List[float]]:
    """
    Benchmark the original and optimized implementations for different matrix sizes.
    
    Args:
        max_activities: Maximum number of activities to test
        trials_per_size: Number of random matrices to generate per size
        timeout_sec: Maximum seconds to wait for a computation before giving up
        
    Returns:
        Tuple of (sizes, original_times, optimized_times)
    """
    sizes = list(range(2, max_activities + 1))
    original_times = []
    optimized_times = []
    
    for size in sizes:
        print(f"Benchmarking matrices with {size} activities...")
        
        size_original_times = []
        size_optimized_times = []
        
        for trial in range(trials_per_size):
            print(f"  Trial {trial + 1}/{trials_per_size}")
            
            matrix = generate_random_matrix(size)
            
            # Benchmark original implementation
            start_time = time.time()
            try:
                original_result = []
                # Use a timeout to prevent very long runs
                if size <= 6:
                    original_result = generate_acceptance_variants(matrix)
                    elapsed = time.time() - start_time
                    size_original_times.append(elapsed)
                    print(f"    Original: {elapsed:.4f} seconds, {len(original_result)} variants")
                else:
                    print(f"    Original: Skipped for size > 6")
                    size_original_times.append(float('inf'))
            except Exception as e:
                print(f"    Original implementation failed: {str(e)}")
                size_original_times.append(float('inf'))
            
            # Benchmark optimized implementation
            start_time = time.time()
            try:
                optimized_result = generate_optimized_acceptance_variants(matrix)
                elapsed = time.time() - start_time
                size_optimized_times.append(elapsed)
                print(f"    Optimized: {elapsed:.4f} seconds, {len(optimized_result)} variants")
                
                # Verify that results match for small sizes
                if size <= 6 and len(original_result) > 0:
                    if sorted([tuple(v) for v in original_result]) != sorted([tuple(v) for v in optimized_result]):
                        print(f"    WARNING: Results do not match for size {size}, trial {trial+1}")
            except Exception as e:
                print(f"    Optimized implementation failed: {str(e)}")
                size_optimized_times.append(float('inf'))
        
        # Average the times for this size
        if any(t != float('inf') for t in size_original_times):
            avg_original = sum(t for t in size_original_times if t != float('inf')) / sum(1 for t in size_original_times if t != float('inf'))
            original_times.append(avg_original)
        else:
            original_times.append(float('inf'))
            
        if any(t != float('inf') for t in size_optimized_times):
            avg_optimized = sum(t for t in size_optimized_times if t != float('inf')) / sum(1 for t in size_optimized_times if t != float('inf'))
            optimized_times.append(avg_optimized)
        else:
            optimized_times.append(float('inf'))
    
    return sizes, original_times, optimized_times


def print_results_table(sizes: List[int], original_times: List[float], optimized_times: List[float]) -> None:
    """Print the benchmark results as a formatted table."""
    print("\nResults:")
    print("Activities | Original Time (s) | Optimized Time (s) | Speedup")
    print("-" * 60)
    
    speedups = calculate_speedup(original_times, optimized_times)
    
    for i, size in enumerate(sizes):
        orig_time = original_times[i]
        opt_time = optimized_times[i]
        speedup = speedups[i]
        
        orig_str = f"{orig_time:.4f}" if orig_time != float('inf') else "timeout"
        opt_str = f"{opt_time:.4f}" if opt_time != float('inf') else "timeout"
        
        if speedup == float('inf'):
            speedup_str = "N/A"
        elif speedup == float('nan'):
            speedup_str = "N/A"
        else:
            speedup_str = f"{speedup:.2f}x"
        
        print(f"{size:9d} | {orig_str:16s} | {opt_str:17s} | {speedup_str}")


def calculate_speedup(original_times: List[float], optimized_times: List[float]) -> List[float]:
    """Calculate the speedup of the optimized implementation compared to the original."""
    speedups = []
    for orig, opt in zip(original_times, optimized_times):
        if orig == float('inf') or opt == float('inf'):
            speedups.append(float('nan'))
        elif orig == 0 or opt == 0:
            # Handle cases with very small times that round to 0
            speedups.append(1.0)  # Assume roughly equal performance
        else:
            speedups.append(orig / opt)
    return speedups


def run_benchmark(max_size: int = 8) -> None:
    """Run the benchmark comparison and print the results."""
    print("Running acceptance variants generation benchmark...")
    sizes, original_times, optimized_times = benchmark_comparison(max_activities=max_size)
    
    print_results_table(sizes, original_times, optimized_times)


if __name__ == "__main__":
    run_benchmark(max_size=9)
