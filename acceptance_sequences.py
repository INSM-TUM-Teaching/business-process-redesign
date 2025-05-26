from itertools import permutations
from typing import List, Tuple, Dict, Set
from dependencies import TemporalType, ExistentialType, TemporalDependency, ExistentialDependency
from adjacency_matrix import AdjacencyMatrix

def satisfies_existential_constraints(
    subset: Set[str],
    activities: List[str],
    existential_dependencies: Dict[Tuple[str, str], ExistentialDependency]
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

            if dep_type == ExistentialType.IMPLICATION:
                if in_subset_ai and not in_subset_aj:
                    return False
            elif dep_type == ExistentialType.EQUIVALENCE:
                if in_subset_ai != in_subset_aj:
                    return False
            elif dep_type == ExistentialType.NEGATED_EQUIVALENCE:
                if in_subset_ai == in_subset_aj:
                    return False
            elif dep_type == ExistentialType.NAND:
                if in_subset_ai and in_subset_aj:
                    return False
            elif dep_type == ExistentialType.OR:
                if not (in_subset_ai or in_subset_aj):
                    return False
            # INDEPENDENCE is handled by the continue above

    return True

def build_permutations(subset: Set[str]) -> List[List[str]]:
    """
    Generates all possible orderings (permutations) of activities in a subset.
    """
    if not subset:
        return [[]]
    return [list(p) for p in permutations(subset)]

def satisfies_temporal_constraints(
    sequence: List[str],
    temporal_dependencies: Dict[Tuple[str, str], TemporalDependency]
) -> bool:
    """
    Checks if a sequence of activities satisfies all temporal constraints.
    """
    if not sequence: # An empty sequence has no temporal constraints to violate
        return True

    activity_to_pos = {activity: i for i, activity in enumerate(sequence)}

    for i in range(len(sequence)):
        for j in range(len(sequence)):
            if i == j:
                continue

            ai = sequence[i]
            aj = sequence[j]

            dependency = temporal_dependencies.get((ai, aj))
            if not dependency or dependency.type == TemporalType.INDEPENDENCE:
                continue # No constraint or independence means satisfied

            pos_ai = activity_to_pos[ai]
            pos_aj = activity_to_pos[aj]
            dep_type = dependency.type


            if dep_type == TemporalType.DIRECT:
                if pos_aj != pos_ai + 1:
                    return False
            elif dep_type == TemporalType.EVENTUAL:
                if pos_ai >= pos_aj:
                    return False
            # INDEPENDENCE is handled by the continue

    return True

def generate_acceptance_sequences(adj_matrix: AdjacencyMatrix) -> List[List[str]]:
    """
    Generates all valid acceptance sequences from an adjacency matrix.
    """
    activities = adj_matrix.activities
    temporal_deps: Dict[Tuple[str, str], TemporalDependency] = {}
    existential_deps: Dict[Tuple[str, str], ExistentialDependency] = {}

    for (source, target), (temp_dep, exist_dep) in adj_matrix.dependencies.items():
        if temp_dep:
            temporal_deps[(source, target)] = temp_dep
        if exist_dep:
            existential_deps[(source, target)] = exist_dep

    acceptance_sequences = []
    n = len(activities)

    for i in range(1 << n): # 2^n subsets
        current_subset_indices = []
        for j in range(n):
            if (i >> j) & 1: # Check if j-th bit is set
                current_subset_indices.append(j)
        
        current_subset_activities = {activities[k] for k in current_subset_indices}

        if satisfies_existential_constraints(current_subset_activities, activities, existential_deps):
            permutations_of_subset = build_permutations(current_subset_activities)
            for seq in permutations_of_subset:
                if satisfies_temporal_constraints(seq, temporal_deps):
                    acceptance_sequences.append(seq)
    
    return acceptance_sequences


# if __name__ == "__main__":
#     adj_matrix = AdjacencyMatrix(activities=["A", "B", "C", "D", "E"])
#     adj_matrix.add_dependency("A", "B", TemporalDependency(TemporalType.DIRECT), ExistentialDependency(ExistentialType.IMPLICATION))
#     adj_matrix.add_dependency("B", "C", TemporalDependency(TemporalType.EVENTUAL), ExistentialDependency(ExistentialType.EQUIVALENCE))
#     adj_matrix.add_dependency("C", "D", TemporalDependency(TemporalType.INDEPENDENCE), ExistentialDependency(ExistentialType.NAND))
#     adj_matrix.add_dependency("D", "E", TemporalDependency(TemporalType.DIRECT), ExistentialDependency(ExistentialType.INDEPENDENCE))
#     acceptance_seqs = generate_acceptance_sequences(adj_matrix)
#     print("Generated Acceptance Sequences:")
#     for seq in acceptance_seqs:
#         print(seq)