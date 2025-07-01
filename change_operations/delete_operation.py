from typing import List, Set
from adjacency_matrix import AdjacencyMatrix
from acceptance_variants import generate_acceptance_variants
from traces_to_matrix import traces_to_adjacency_matrix
from dependencies import ExistentialType


def delete_activity_from_variants(
    variants: List[List[str]], activity: str, remove_duplicates: bool = False
) -> List[List[str]]:
    """
    Removes the specified activity from all acceptance variants.

    Args:
        variants: List of variants to process
        activity: Activity to remove from all variants
        remove_duplicates: If True, removes duplicate variants after removing the activity

    Returns:
        New variants with the activity removed, with or without duplicates based on remove_duplicates
    """
    modified_variants = []
    seen = set()

    for variant in variants:
        # Remove activity from variant if present
        modified_variant = [act for act in variant if act != activity]
        # Only add non-empty variants
        if modified_variant:
            if remove_duplicates:
                variant_tuple = tuple(modified_variant)
                if variant_tuple not in seen:
                    seen.add(variant_tuple)
                    modified_variants.append(modified_variant)
            else:
                modified_variants.append(modified_variant)

    return modified_variants


def delete_activity(matrix: AdjacencyMatrix, activity: str) -> AdjacencyMatrix:
    """
    Deletes an activity from the process by:
    1. Checking if deletion would result in an empty process due to equivalence relationships
    2. Generating acceptance variants from the input matrix
    3. Removing the activity from all variants
    4. Converting modified variants back to a matrix

    Args:
        matrix: The input adjacency matrix
        activity: The name of the activity to delete

    Returns:
        A new adjacency matrix with the activity removed

    Raises:
        ValueError: If activity not found or deletion would result in empty process
    """
    if activity not in matrix.activities:
        raise ValueError(f"Activity {activity} not found in matrix")

    if would_result_in_empty_process(matrix, activity):
        raise ValueError(
            "Deletion would result in empty process due to equivalence relationships"
        )

    # Generate variants from input matrix
    variants = generate_acceptance_variants(matrix)

    # Remove activity from variants
    modified_variants = delete_activity_from_variants(variants, activity)

    if not modified_variants:
        raise ValueError("Deletion would result in empty process")

    # Convert modified variants back to matrix
    # Remove the activity from the list first to ensure it's not included
    new_activities = [act for act in matrix.activities if act != activity]
    new_matrix = traces_to_adjacency_matrix(modified_variants, 1.0, 1.0)

    return new_matrix


def would_result_in_empty_process(matrix: AdjacencyMatrix, activity: str) -> bool:
    """
    Checks if deleting the activity would result in an empty process due to equivalence relationships.
    """
    for (source, target), (_, exist_dep) in matrix.dependencies.items():
        if exist_dep and exist_dep.type == ExistentialType.EQUIVALENCE:
            if source == activity or target == activity:
                # If either activity in an equivalence relationship is deleted,
                # the other must be deleted too due to the relationship
                other_activity = target if source == activity else source
                # Check if this would cascade to deleting all activities
                connected_activities = {source, target}
                for (s, t), (_, e) in matrix.dependencies.items():
                    if e and e.type == ExistentialType.EQUIVALENCE:
                        if s in connected_activities or t in connected_activities:
                            connected_activities.add(s)
                            connected_activities.add(t)
                # If all activities are connected by equivalence, deleting one would empty the process
                if connected_activities.issuperset(set(matrix.activities)):
                    return True
    return False
