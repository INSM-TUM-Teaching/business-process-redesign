from typing import Tuple, Optional, Dict, List, Set
from dependencies import (
    TemporalDependency,
    ExistentialDependency,
    TemporalType,
)
from adjacency_matrix import AdjacencyMatrix
from acceptance_variants import generate_acceptance_variants, satisfies_existential_constraints
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
        return False
    if has_existential_contradiction(existential_deps):
        return  False
    if has_temporal_contradiction(temporal_deps):
        return False
    return True

def determine_set_before(temporal_deps: Dict[Tuple[str, str], TemporalDependency], cur_activity: str, cur_activities_before: Set[str] = set()):
    for temporal_dep in temporal_deps:
        if temporal_deps.get(temporal_dep).type == TemporalType.INDEPENDENCE:
            continue
        (before, after) = temporal_dep
        if after == cur_activity:
            cur_activities_before.add(before)
            cur_activities_before = cur_activities_before | determine_set_before(temporal_deps, before, cur_activities_before)
    return cur_activities_before

def determine_set_after(temporal_deps, cur_activity, cur_activities_after: Set[str] = set()):
    for temporal_dep in temporal_deps:
        if temporal_deps.get(temporal_dep).type == TemporalType.INDEPENDENCE:
            continue
        (before, after) = temporal_dep
        if before == cur_activity:
            cur_activities_after.add(after)
            cur_activities_after = cur_activities_after | determine_set_after(temporal_deps, after, cur_activities_after)
    return cur_activities_after

def search_valid_positions_to_insert(variant: List[str], activity: str, activities_before, activities_after, direct_before, direct_after) -> List[List[str]]:
    variants: List[List[str]] = []

    #Check if there exists activity which has direct temporal relation
    for a in direct_before:
        if a in variant:
            pos_before = variant.index(a)
            new_variant = variant.copy()
            new_variant.insert(pos_before+1, activity)
            variants.append(new_variant)
            return variants
    for a in direct_after:
        if a in variant:
            pos_after = variant.index(a)
            new_variant = variant.copy()
            new_variant.insert(pos_after, activity)
            variants.append(new_variant)
            return variants

    #Insert depending on set before and after
    for a in reversed(variant):
        if a in activities_before:
            pos_last_before = variant.index(a)
            new_variant = variant.copy()
            new_variant.insert(pos_last_before+1, activity)
            variants.append(new_variant)
            break
    for a in variant:
        if a in activities_after:
            pos_first_after = variant.index(a)
            new_variant = variant.copy()
            new_variant.insert(pos_first_after, activity)
            variants.append(new_variant)
            break
    return variants

def insert_activity(
    matrix: AdjacencyMatrix,
    activity: str,
    dependencies: Dict[
        Tuple[str, str],
        Tuple[Optional[TemporalDependency], Optional[ExistentialDependency]],
    ]) -> AdjacencyMatrix:
    """
    Adds a new acivity to the process by:
    1. Checking if input is valid.
    2. Getting the sets of activities before/after and directly before/after.
    3. Generating variants for the input matrix.
    4. Checking if for variant existential dependencies hold with and without activity to be inserted.
    5. Inserting accroding to direct or eventual temporal dependencies.

    Args:
        matrix: The input adjacency matrix
        activity: The name of the activity to insert
        dependencies: The dependencies defining the position of the activity to be inserted

    Returns:
        A new adjacency matrix with the activity inserted

    Raises:
        ValueError: If input is produces contradiction
    """
    print("Start insert")

    total_temporal_deps: Dict[Tuple[str, str], TemporalDependency] = {}
    total_existential_deps: Dict[Tuple[str, str], ExistentialDependency] = {}

    temporal_deps: Dict[Tuple[str, str], TemporalDependency] = {}
    existential_deps: Dict[Tuple[str, str], ExistentialDependency] = {}

    new_dependencies =  matrix.get_dependencies() | dependencies

    for (source, target), (temp_dep, exist_dep) in new_dependencies.items():
        if temp_dep:
            total_temporal_deps[(source, target)] = temp_dep
        if exist_dep:
            total_existential_deps[(source, target)] = exist_dep

    for (source, target), (temp_dep, exist_dep) in dependencies.items():
        if temp_dep:
            temporal_deps[(source, target)] = temp_dep
        if exist_dep:
            existential_deps[(source, target)] = exist_dep
    

    if not is_valid_input(matrix, activity, total_temporal_deps, total_existential_deps):
        raise ValueError("The input is invalid.")

    new_activities = matrix.get_activities().copy()
    new_activities.append(activity)
    

    activities_before = determine_set_before(total_temporal_deps, activity)
    activities_after = determine_set_after(total_temporal_deps, activity)

    direct_before = []
    direct_after = []

    for dependency in temporal_deps:
        if temporal_deps.get(dependency).type == TemporalType.DIRECT:
            (before, after) = dependency
            if activity == before:
                direct_after.append(after)
            if activity == after:
                direct_before.append(before)

    variants = generate_acceptance_variants(matrix)

    new_variants = []

    if satisfies_existential_constraints(set(activity), new_activities, total_existential_deps):
        new_variants.append([activity])

    for variant in variants:
        if satisfies_existential_constraints(set(variant), new_activities, existential_deps):
            new_variants.append(variant)
        variant_with_activity = variant.copy()
        variant_with_activity.append(activity)
        if not satisfies_existential_constraints(set(variant_with_activity), new_activities, existential_deps):
            continue
        valid_variants = search_valid_positions_to_insert(variant, activity, activities_before, activities_after, direct_before, direct_after)
        new_variants.extend(valid_variants)

    new_matrix = traces_to_adjacency_matrix(new_variants)

    return new_matrix