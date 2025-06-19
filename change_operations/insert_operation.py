from typing import Tuple, Optional, Dict, List
from dependencies import (
    TemporalDependency,
    ExistentialDependency,
    TemporalType,
    ExistentialType
)
from constraint_logic import check_existential_relationship, check_temporal_relationship
from adjacency_matrix import AdjacencyMatrix
from acceptance_variants import (
    build_permutations
)
from traces_to_matrix import traces_to_adjacency_matrix

def has_existential_contradiction(existential_deps: Dict[Tuple[str, str], ExistentialDependency]) -> bool:
    return False


def has_temporal_contradiction(temporal_deps):
    """
    Checks if temporal ordering has contradictions. Handles direct as eventual temporal dependencies, since insert might change it.

    Missing
    """
    
    return False

def is_valid_input(matrix: AdjacencyMatrix,
    activity: str,
    temporal_deps: Dict[Tuple[str, str], TemporalDependency] = {},
    existential_deps: Dict[Tuple[str, str], ExistentialDependency] = {}
    ) -> bool:
    
    if activity in matrix.get_activities():
        print(activity, matrix.get_activities())
        return False
    if has_existential_contradiction(existential_deps):
        return  False
    if has_temporal_contradiction(temporal_deps):
        return False
    return True

def insert_activity(
    matrix: AdjacencyMatrix,
    activity: str,
    dependencies: Dict[
        Tuple[str, str],
        Tuple[Optional[TemporalDependency], Optional[ExistentialDependency]],
    ]) -> AdjacencyMatrix:
    """
    Adds a new acivity to the process by:
    1.

    Args:
        matrix: The input adjacency matrix
        activity: The name of the activity to insert
        dependencies: The dependencies defining the position of the activity to be inserted

    Returns:
        A new adjacency matrix with the activity inserted

    Raises:

    """
    print("Start insert")

    temporal_deps: Dict[Tuple[str, str], TemporalDependency] = {}
    existential_deps: Dict[Tuple[str, str], ExistentialDependency] = {}

    new_dependencies =  matrix.get_dependencies() | dependencies


    for (source, target), (temp_dep, exist_dep) in new_dependencies.items():
        if temp_dep:
            temporal_deps[(source, target)] = temp_dep
        if exist_dep:
            existential_deps[(source, target)] = exist_dep
    
    if not is_valid_input(matrix, activity, temporal_deps, existential_deps):
        raise ValueError("The input is invalid.")

    activities = matrix.get_activities() or []
    activities.append(activity)

    permutations = build_permutations(activities)

    variants = []

    for variant in permutations:
        is_valid = True
        for dependency in existential_deps:
            (source, target) = dependency
            source_present = source in variant
            target_present = target in variant
            if not check_existential_relationship(source_present, target_present, ExistentialType.EQUIVALENCE):
                is_valid = False
                break
        if not is_valid:
            continue
        for dependency in temporal_deps:
            relationship = temporal_deps.get(dependency)
            (source, target) = dependency
            source_pos = variant.index(source)
            target_pos = variant.index(target)
            if not check_temporal_relationship(source_pos, target_pos, relationship.type):
                is_valid = False
                break
        if is_valid:
            variants.append(variant)

    print(variants)

    new_matrix = traces_to_adjacency_matrix(variants)

    print(new_matrix)

    return new_matrix
