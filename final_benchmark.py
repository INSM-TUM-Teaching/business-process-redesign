import sys
import time
import random
import numpy as np
from typing import List, Dict, Tuple

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

# Create charts only if matplotlib is available
try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Matplotlib not available. Charts won't be generated.")

def generate_complex_matrix(n_activities: int, complexity: float = 0.3) -> AdjacencyMatrix:
    """Generate a test matrix with controlled complexity."""
    activities = [chr(65 + i) for i in range(min(n_activities, 26))]
    if n_activities > 26:
        activities.extend([f"A{i}" for i in range(n_activities - 26)])
    
    matrix = AdjacencyMatrix(activities=activities)
    
    for i in range(n_activities - 1):
        matrix.add_dependency(
            activities[i],
            activities[i+1],
            TemporalDependency(TemporalType.DIRECT, Direction.FORWARD),
            None
        )
    
    # Add more dependencies based on complexity parameter
    max_deps = int((n_activities * (n_activities - 1) / 2) * complexity)
    deps_added = n_activities - 1  # Count the ones already added
    
    # Generate all possible pairs
    pairs = [(i, j) for i in range(n_activities) for j in range(n_activities) if i != j and j != i+1]
    random.shuffle(pairs)
    
    for i, j in pairs:
        if deps_added >= max_deps:
            break
            
        # Skip if we already have a dependency
        if matrix.get_dependency(activities[i], activities[j]) is not None:
            continue
        
        # Randomly choose dependency types
        if random.random() < 0.7:
            temp_type = random.choice([TemporalType.EVENTUAL, TemporalType.INDEPENDENCE])
            temp_dir = random.choice([Direction.FORWARD, Direction.BACKWARD, Direction.BOTH])
            temp_dep = TemporalDependency(temp_type, temp_dir)
        else:
            temp_dep = None
            
        if random.random() < 0.7:
            exist_type = random.choice([
                ExistentialType.IMPLICATION, 
                ExistentialType.EQUIVALENCE,
                ExistentialType.OR,
                ExistentialType.NAND,
                ExistentialType.INDEPENDENCE
            ])
            exist_dir = Direction.BOTH
            if exist_type == ExistentialType.IMPLICATION:
                exist_dir = random.choice([Direction.FORWARD, Direction.BACKWARD, Direction.BOTH])
            exist_dep = ExistentialDependency(exist_type, exist_dir)
        else:
            exist_dep = None
            
        if temp_dep or exist_dep:
            matrix.add_dependency(activities[i], activities[j], temp_dep, exist_dep)
            deps_added += 1
    
    return matrix

def run_comprehensive_benchmark(max_size: int = 17, repetitions: int = 2, timeout_sec: int = 30):
    """
    Run a comprehensive benchmark comparing original and optimized implementations.
    
    Args:
        max_size: Maximum matrix size to test
        repetitions: Number of times to repeat each test for more stable results
        timeout_sec: Maximum seconds to wait for the original implementation
    """
    # Set random seed for reproducibility
    random.seed(42)
    
    import platform
    is_windows = platform.system() == 'Windows' # Detect platform for proper timeout handling
    
    if is_windows:
        import threading
    else:
        import signal
    
    sizes = list(range(3, max_size + 1))
    results = {
        'sizes': sizes,
        'original': {
            'times': [],
            'variants': []
        },
        'optimized': {
            'times': [],
            'variants': []
        },
        'speedups': []
    }
    
    for size in sizes:
        print(f"\nBenchmarking size {size}...")
        
        size_original_times = []
        size_optimized_times = []
        size_original_variants = []
        size_optimized_variants = []
        
        for rep in range(repetitions):
            # Adjust complexity based on size - decrease complexity more aggressively for larger sizes
            if size <= 8:
                complexity = min(0.3, 3.0 / size)
            elif size <= 12:
                complexity = min(0.2, 2.0 / size)
            else:
                complexity = min(0.15, 1.5 / size)
                
            print(f"  Using complexity factor: {complexity:.4f}")
            matrix = generate_complex_matrix(size, complexity)
            
            # Skip original for large sizes to avoid long wait times
            if size <= 12:  # Test original up to size 12
                print(f"  Running original implementation (rep {rep+1}/{repetitions})...")
                
                if is_windows:
                    class TimeoutException(Exception):
                        pass
                    
                    def run_with_timeout():
                        nonlocal size_original_times, size_original_variants
                        try:
                            start_time = time.time()
                            original_variants = generate_acceptance_variants(matrix)
                            elapsed_time = time.time() - start_time
                            
                            size_original_times.append(elapsed_time)
                            size_original_variants.append(len(original_variants))
                            print(f"    Time: {elapsed_time:.6f}s, Variants: {len(original_variants)}")
                            return True
                        except Exception as e:
                            print(f"    Failed: {str(e)}")
                            return False
                    
                    thread_result = [False]
                    thread = threading.Thread(target=lambda: thread_result.__setitem__(0, run_with_timeout()))
                    thread.daemon = True
                    thread.start()
                    thread.join(timeout_sec)
                    
                    if thread.is_alive():
                        print(f"    Timed out after {timeout_sec} seconds")
                        print("    Warning: Thread is still running in the background and cannot be forcibly terminated safely.")
                else:
                    # For Unix systems: Use the signal module
                    try:
                        def timeout_handler(signum, frame):
                            raise TimeoutError(f"Execution timed out after {timeout_sec} seconds")
                        
                        signal.signal(signal.SIGALRM, timeout_handler)
                        signal.alarm(timeout_sec)
                        
                        try:
                            start_time = time.time()
                            original_variants = generate_acceptance_variants(matrix)
                            elapsed_time = time.time() - start_time
                            
                            # Cancel the alarm as we completed in time
                            signal.alarm(0)
                            
                            original_time = elapsed_time
                            size_original_times.append(original_time)
                            size_original_variants.append(len(original_variants))
                            
                            print(f"    Time: {original_time:.6f}s, Variants: {len(original_variants)}")
                        except TimeoutError:
                            print(f"    Timed out after {timeout_sec} seconds")
                            signal.alarm(0)  # Cancel the alarm
                        except Exception as e:
                            print(f"    Failed: {str(e)}")
                            signal.alarm(0)  # Cancel the alarm
                    except Exception as e:
                        print(f"    Signal handling failed: {str(e)}")
            else:
                print(f"  Skipping original implementation for size {size}")
            
            # Always run optimized
            print(f"  Running optimized implementation (rep {rep+1}/{repetitions})...")
            try:
                start_time = time.time()
                optimized_variants = generate_optimized_acceptance_variants(matrix)
                optimized_time = time.time() - start_time
                
                size_optimized_times.append(optimized_time)
                size_optimized_variants.append(len(optimized_variants))
                
                print(f"    Time: {optimized_time:.6f}s, Variants: {len(optimized_variants)}")
            except Exception as e:
                print(f"    Failed: {str(e)}")
        
        # Average the results
        if size_original_times:
            avg_original_time = sum(size_original_times) / len(size_original_times)
            avg_original_variants = sum(size_original_variants) / len(size_original_variants)
            results['original']['times'].append(avg_original_time)
            results['original']['variants'].append(avg_original_variants)
        else:
            results['original']['times'].append(None)
            results['original']['variants'].append(None)
        
        if size_optimized_times:
            avg_optimized_time = sum(size_optimized_times) / len(size_optimized_times)
            avg_optimized_variants = sum(size_optimized_variants) / len(size_optimized_variants)
            results['optimized']['times'].append(avg_optimized_time)
            results['optimized']['variants'].append(avg_optimized_variants)
        else:
            results['optimized']['times'].append(None)
            results['optimized']['variants'].append(None)
        
        # Calculate speedup
        if (results['original']['times'][-1] is not None and 
            results['optimized']['times'][-1] is not None and
            results['optimized']['times'][-1] > 0):
            speedup = results['original']['times'][-1] / results['optimized']['times'][-1]
            results['speedups'].append(speedup)
        else:
            results['speedups'].append(None)
    
    print("\n===== RESULTS =====")
    print(f"{'Size':<5} {'Original (s)':<14} {'Optimized (s)':<14} {'Speedup':<10} {'Variants'}")
    print("-" * 65)
    
    for i, size in enumerate(results['sizes']):
        orig_time = results['original']['times'][i]
        opt_time = results['optimized']['times'][i]
        speedup = results['speedups'][i]
        variants = results['optimized']['variants'][i] or results['original']['variants'][i] or "N/A"
        
        orig_time_str = f"{orig_time:.6f}" if orig_time is not None else "N/A"
        opt_time_str = f"{opt_time:.6f}" if opt_time is not None else "N/A"
        speedup_str = f"{speedup:.2f}x" if speedup is not None else "N/A"
        
        print(f"{size:<5} {orig_time_str:<14} {opt_time_str:<14} {speedup_str:<10} {variants}")
    
    # Create chart if matplotlib is available
    if HAS_MATPLOTLIB:
        create_charts(results)

def create_charts(results):
    """Create performance charts from benchmark results."""
    plt.figure(figsize=(12, 10))
    
    sizes = results['sizes']
    original_times = results['original']['times']
    optimized_times = results['optimized']['times']
    
    # Filter out None values for comparison
    valid_indices = [i for i, (o, p) in enumerate(zip(original_times, optimized_times)) 
                    if o is not None and p is not None]
    valid_sizes = [sizes[i] for i in valid_indices]
    valid_original = [original_times[i] for i in valid_indices]
    valid_optimized = [optimized_times[i] for i in valid_indices]
    
    # Get all optimized results (including where original is missing)
    all_opt_indices = [i for i, p in enumerate(optimized_times) if p is not None]
    all_opt_sizes = [sizes[i] for i in all_opt_indices]
    all_opt_times = [optimized_times[i] for i in all_opt_indices]
    
    # Plot execution times
    plt.subplot(2, 1, 1)
    
    # Plot optimized times for all available sizes
    plt.plot(all_opt_sizes, all_opt_times, 's-', label='Optimized', color='#1F77B4')
    
    # Plot original times where available
    if valid_indices:
        plt.plot(valid_sizes, valid_original, 'o-', label='Original', color='#FF7F0E')
    
    plt.yscale('log')
    plt.grid(True, alpha=0.3)
    plt.xlabel('Number of Activities')
    plt.ylabel('Time (seconds) - Log Scale')
    plt.title('Acceptance Variants Generation Performance')
    plt.legend()
    
    # Plot speedup where we have both implementations
    if valid_indices:
        plt.subplot(2, 1, 2)
        # Check for division by zero
        speedups = [o / p if p > 0 else float('inf') for o, p in zip(valid_original, valid_optimized)]
        plt.bar(valid_sizes, speedups, color='#2CA02C')
        plt.grid(True, alpha=0.3)
        plt.xlabel('Number of Activities')
        plt.ylabel('Speedup (Original/Optimized)')
        plt.title('Performance Speedup Factor')
        
        for i, v in enumerate(speedups):
            if not np.isinf(v):  # Skip infinite values
                plt.text(valid_sizes[i], v + 0.1, f'{v:.1f}x', ha='center')
        
        plt.tight_layout()
        plt.savefig('benchmark_results.png')
        print("\nPerformance chart saved to 'benchmark_results.png'")

if __name__ == "__main__":
    if not HAS_MATPLOTLIB:
        try:
            import subprocess
            print("Installing matplotlib...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib"])
            import matplotlib.pyplot as plt
            HAS_MATPLOTLIB = True
        except:
            print("Failed to install matplotlib. Charts won't be generated.")
    
    run_comprehensive_benchmark(max_size=17, repetitions=2, timeout_sec=30)
