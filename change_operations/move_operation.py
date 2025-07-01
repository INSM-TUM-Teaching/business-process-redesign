from typing import Tuple, Optional, Dict, List
from dependencies import (
    TemporalDependency,
    ExistentialDependency,
)
from adjacency_matrix import AdjacencyMatrix
from acceptance_variants import (
    generate_acceptance_variants,
)
from traces_to_matrix import traces_to_adjacency_matrix
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
    total_dependencies = matrix.get_dependencies() | dependencies
    activities = matrix.get_activities().copy()
        

    variants = generate_acceptance_variants(matrix)
    new_variants = move_activity_in_variants(activity, dependencies, variants, activities, total_dependencies)
    return  traces_to_adjacency_matrix(new_variants)

def move_activity_in_variants(
        activity: str,
        dependencies: Dict[
            Tuple[str, str],
            Tuple[Optional[TemporalDependency], Optional[ExistentialDependency]],
        ],
        variants: List[List[str]],
        activities: List[str],
        total_dependencies: Dict[
            Tuple[str, str],
            Tuple[Optional[TemporalDependency], Optional[ExistentialDependency]],
        ]
    ) -> List[List[str]]:
    """
    Removes activity from original position and moves it to new position.

    Args:
        activity: The name of the activity which should be moved
        dependencies: The dependencies defining the new position of the activity to be moved
        variants: The variants of the original matrix
        activities: Activities of original matrix
        total_dependencies: Dependencies which also include all the dependencies from the original matrix

    Returns:
        A new adjacency matrix with the activity moved

    Raises:
        ValueError: If input produces contradiction
    """
    
    new_variants = delete_activity_from_variants(variants, activity, True)

    dependencies_after_delete = dict()

    for (source, target) in total_dependencies:
        if (source == activity) or (target == activity):
            continue
        dependencies_after_delete[(source,target)] = total_dependencies.get((source,target))
    activities.remove(activity)
    new_variants = insert_into_variants(activity, dependencies, dependencies_after_delete, activities, new_variants)

    return new_variants