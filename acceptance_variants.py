from itertools import permutations
from typing import List, Tuple, Dict, Set
from dependencies import (
    TemporalType,
    ExistentialType,
    TemporalDependency,
    ExistentialDependency,
)
from adjacency_matrix import AdjacencyMatrix
from constraint_logic import check_temporal_relationship, check_existential_relationship


def satisfies_existential_constraints(
    subset: Set[str],
    activities: List[str],
    existential_dependencies: Dict[Tuple[str, str], ExistentialDependency],
) -> bool:
    """
    Checks if a subset of activities satisfies all existential constraints.
    """
    activity_to_index = {activity: i for i, activity in enumerate(activities)}

    for i in range(len(activities)):
        for j in range(len(activities)):
            ai = activities[i]
            aj = activities[j]

            dependency = existential_dependencies.get((ai, aj))
            # Skip if the dependency is not defined for the pair (ai, aj)
            # or if it's an independence constraint (which is always satisfied by any subset)
            if not dependency or dependency.type == ExistentialType.INDEPENDENCE:
                continue

            in_subset_ai = ai in subset
            in_subset_aj = aj in subset
            dep_type = dependency.type

            if not check_existential_relationship(in_subset_ai, in_subset_aj, dep_type):
                return False

    return True


def build_permutations(subset: Set[str]) -> List[List[str]]:
    """
    Generates all possible orderings (permutations) of activities in a subset.
    """
    if not subset:
        return [[]]
    return [list(p) for p in permutations(subset)]


def satisfies_temporal_constraints(
    variant: List[str],
    temporal_dependencies: Dict[Tuple[str, str], TemporalDependency],
) -> bool:
    """
    Checks if a variant of activities satisfies all temporal constraints.
    """
    if not variant:  # An empty variant has no temporal constraints to violate
        return True

    activity_to_pos = {activity: i for i, activity in enumerate(variant)}

    for i in range(len(variant)):
        for j in range(len(variant)):
            if i == j:
                continue

            ai = variant[i]
            aj = variant[j]

            dependency = temporal_dependencies.get((ai, aj))
            if not dependency or dependency.type == TemporalType.INDEPENDENCE:
                continue  # No constraint or independence means satisfied

            pos_ai = activity_to_pos[ai]
            pos_aj = activity_to_pos[aj]
            dep_type = dependency.type

            if not check_temporal_relationship(pos_ai, pos_aj, dep_type):
                return False

    return True


def generate_acceptance_variants(adj_matrix: AdjacencyMatrix) -> List[List[str]]:
    """
    Generates all valid acceptance variants from an adjacency matrix.
    """
    activities = adj_matrix.activities
    temporal_deps: Dict[Tuple[str, str], TemporalDependency] = {}
    existential_deps: Dict[Tuple[str, str], ExistentialDependency] = {}

    for (source, target), (temp_dep, exist_dep) in adj_matrix.dependencies.items():
        if temp_dep:
            temporal_deps[(source, target)] = temp_dep
        if exist_dep:
            existential_deps[(source, target)] = exist_dep

    acceptance_variants = []
    n = len(activities)

    for i in range(1 << n):  # 2^n subsets
        current_subset_indices = []
        for j in range(n):
            if (i >> j) & 1:  # Check if j-th bit is set
                current_subset_indices.append(j)

        current_subset_activities = {activities[k] for k in current_subset_indices}

        if satisfies_existential_constraints(
            current_subset_activities, activities, existential_deps
        ):
            permutations_of_subset = build_permutations(current_subset_activities)
            for seq in permutations_of_subset:
                if satisfies_temporal_constraints(seq, temporal_deps):
                    acceptance_variants.append(seq)

    return acceptance_variants


# if __name__ == "__main__":
#     adj_matrix = AdjacencyMatrix(activities=["A", "B", "C", "D", "E"])
#     adj_matrix.add_dependency("A", "B", TemporalDependency(TemporalType.DIRECT), ExistentialDependency(ExistentialType.IMPLICATION))
#     adj_matrix.add_dependency("B", "C", TemporalDependency(TemporalType.EVENTUAL), ExistentialDependency(ExistentialType.EQUIVALENCE))
#     adj_matrix.add_dependency("C", "D", TemporalDependency(TemporalType.INDEPENDENCE), ExistentialDependency(ExistentialType.NAND))
#     adj_matrix.add_dependency("D", "E", TemporalDependency(TemporalType.DIRECT), ExistentialDependency(ExistentialType.INDEPENDENCE))
#     acceptance_vars = generate_acceptance_variants(adj_matrix)
#     print("Generated Acceptance Variants:")
#     for var in acceptance_vars:
#         print(var)
