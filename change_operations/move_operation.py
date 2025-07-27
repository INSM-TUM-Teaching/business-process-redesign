from typing import Tuple, Optional, Dict, List
from dependencies import (
    TemporalDependency,
    ExistentialDependency,
)
from adjacency_matrix import AdjacencyMatrix
from optimized_acceptance_variants import generate_optimized_acceptance_variants as generate_acceptance_variants
from variants_to_matrix import variants_to_matrix
from change_operations.delete_operation import delete_activity_from_variants
from change_operations.insert_operation import insert_into_variants

def move_activity(
        matrix: AdjacencyMatrix,
        activity: str,
        dependencies: Dict[
            Tuple[str, str],
            Tuple[Optional[TemporalDependency], Optional[ExistentialDependency]],
        ],
    ) -> AdjacencyMatrix:
    """
    Removes activity from original position and moves it to new position.

    Args:
        matrix: The input adjacency matrix
        activity: The name of the activity which should be moved
        dependencies: The dependencies defining the new position of the activity to be moved

    Returns:
        A new adjacency matrix with the activity moved

    Raises:
        ValueError: If input produces contradiction
    """
    variants = generate_acceptance_variants(matrix)
    try:
        new_variants = move_activity_in_variants(activity, dependencies, variants)
    except ValueError as e:
        raise ValueError(f"The input is invalid: {str(e)}") from e
    return  variants_to_matrix(new_variants, matrix.activities)

def move_activity_in_variants(
        activity: str,
        dependencies: Dict[
            Tuple[str, str],
            Tuple[Optional[TemporalDependency], Optional[ExistentialDependency]],
        ],
        variants: List[List[str]],
    ) -> List[List[str]]:
    """
    Removes activity from original position and moves it to new position.

    Args:
        activity: The name of the activity which should be moved
        dependencies: The dependencies defining the new position of the activity to be moved
        variants: The variants of the original matrix

    Returns:
        A new adjacency matrix with the activity moved

    Raises:
        ValueError: If input produces contradiction
    """
    variants_after_delete = delete_activity_from_variants(variants, activity)
    matrix_after_delete = variants_to_matrix(variants_after_delete)

    total_dependencies = matrix_after_delete.get_dependencies() | dependencies
    try:
        new_variants = insert_into_variants(activity, dependencies, total_dependencies , matrix_after_delete.activities, variants_after_delete)
    except ValueError as e:
        raise ValueError(f"The input is invalid: {e}")

    return new_variants