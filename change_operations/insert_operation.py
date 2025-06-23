from typing import Tuple, Optional, Dict, List, Set
from z3 import Solver, Bool, Implies, Xor, Not, And, Or, sat
from dependencies import (
    TemporalDependency,
    ExistentialDependency,
    TemporalType,
    ExistentialType,
)
from adjacency_matrix import AdjacencyMatrix
from acceptance_variants import (
    generate_acceptance_variants,
    satisfies_existential_constraints,
    satisfies_temporal_constraints,
)
from traces_to_matrix import traces_to_adjacency_matrix


def has_existential_contradiction(
    existential_deps: Dict[Tuple[str, str], ExistentialDependency],
) -> bool:
    """
    Checks if existential dependencies have contradictions.
    """
    solver = Solver()
    variables = {}

    # Collect all activity names
    activity_names = set()
    for a, b in existential_deps.keys():
        activity_names.update([a, b])

    # Create z3 Boolean variables
    for name in activity_names:
        variables[name] = Bool(name)

    # Add constraints
    for (a, b), dep in existential_deps.items():
        var_a = variables[a]
        var_b = variables[b]

        if dep.type == ExistentialType.IMPLICATION:
            constraint = Implies(var_a, var_b)
        elif dep.type == ExistentialType.EQUIVALENCE:
            constraint = var_a == var_b
        elif dep.type == ExistentialType.NEGATED_EQUIVALENCE:
            constraint = Xor(var_a, var_b)
        elif dep.type == ExistentialType.NAND:
            constraint = Not(And(var_a, var_b))
        elif dep.type == ExistentialType.OR:
            constraint = Or(var_a, var_b)
        elif dep.type == ExistentialType.INDEPENDENCE:
            constraint = True  # No constraint
        else:
            raise ValueError(f"Unknown dependency type: {dep.type}")

        solver.add(constraint)

    result = solver.check()
    return not (result == sat)


def dfs(
    temporal_deps: Dict[Tuple[str, str], TemporalDependency],
    cur_activity: str,
    visited: Set[str]
):
    """
    Depth first search returning all activities which have to happen before given activity
    """
    for temporal_dep in temporal_deps:
        if temporal_deps.get(temporal_dep).type == TemporalType.INDEPENDENCE:
            continue
        (before, after) = temporal_dep
        if after == cur_activity:
            if before in visited:
                raise RecursionError
            visited.add(before)
            visited = visited | dfs(temporal_deps, before, visited)
    return visited


def has_temporal_contradiction(
    temporal_deps: Dict[Tuple[str, str], TemporalDependency],
    activities: List[str],
    activity: str,
    variants: List[List[str]],
):
    """
    Checks if temporal ordering has contradictions. Handles direct as eventual temporal dependencies, since insert might change it.
    """
    # Check direct contradiction
    # activity direct to 2 activities with something in between in one of the variants

    after = set()
    before = set()
    for source, target in temporal_deps:
        if temporal_deps.get((source, target)).type != TemporalType.DIRECT:
            continue
        if target == activity:
            before.add(source)
        if source == activity:
            after.add(target)

    for variant in variants:
        # check if there is max 1 before and max 1 after in each variant
        # check if nothing between before and after
        n = 0
        b_pos = -1
        for b in before:
            if b in variant:
                b_pos = variant.index(b)
                n += 1
            if n > 1:
                return True
        n = 0
        a_pos = -1
        for a in after:
            if a in variant:
                a_pos = variant.index(a)
                n += 1
            if n > 1:
                return True
        if (a_pos != -1) and (b_pos != -1):
            if a_pos != (b_pos + 1):
                return True
    # Check for loops
    try:
        for a in activities:
            dfs(temporal_deps, a, set())
    except RecursionError:
        return True

    return False


def is_valid_input(
    matrix: AdjacencyMatrix,
    activities,
    activity: str,
    variants: List[List[str]],
    total_dependencies: Dict[
        Tuple[str, str],
        Tuple[Optional[TemporalDependency], Optional[ExistentialDependency]],
    ],
) -> bool:
    """
    Checks if input is valid

    Args:
        matrix: The input adjacency matrix.
        activities: All activities in matrix and activity to be inserted.
        activity: The name of the activity to insert.
        variants: All variants reslting from matrix.
        dependencies: The dependencies defining the position of the activity to be inserted.

    Returns:
        True: If input is valid
        False: If input is invalid
    """
    total_temporal_deps: Dict[Tuple[str, str], TemporalDependency] = {}
    total_existential_deps: Dict[Tuple[str, str], ExistentialDependency] = {}

    for (source, target), (temp_dep, exist_dep) in total_dependencies.items():
        if temp_dep:
            total_temporal_deps[(source, target)] = temp_dep
        if exist_dep:
            total_existential_deps[(source, target)] = exist_dep

    if activity in matrix.get_activities():
        return False
    if has_existential_contradiction(total_existential_deps):
        return False
    if has_temporal_contradiction(total_temporal_deps, activities, activity, variants):
        return False
    return True


def search_valid_positions_to_insert(
    variant: List[str],
    activity: str,
    temporal_deps: Dict[Tuple[str, str], TemporalDependency],
) -> List[List[str]]:
    """
    Searches all options where activity can be inserted according to temporal dependencies.

    Args:
        variant: variant in which activity shall be inserted
        activity: The name of the activity to insert.
        temporal_dependeps: The temporal dependencies defining the position of the activity to be inserted.

    Returns:
        List of new variants according to temporal dependencies
    """
    new_variants: List[List[str]] = []

    # Insert at any position and check if temporals are fullfilled
    for pos in range(len(variant) + 1):
        new_variant = variant.copy()
        new_variant.insert(pos, activity)
        if satisfies_temporal_constraints(new_variant, temporal_deps):
            new_variants.append(new_variant.copy())
    return new_variants


def insert_activity(
    matrix: AdjacencyMatrix,
    activity: str,
    dependencies: Dict[
        Tuple[str, str],
        Tuple[Optional[TemporalDependency], Optional[ExistentialDependency]],
    ],
) -> AdjacencyMatrix:
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
    variants = generate_acceptance_variants(matrix)

    new_activities = matrix.get_activities().copy()
    new_activities.append(activity)

    total_dependencies = matrix.get_dependencies() | dependencies

    if not is_valid_input(
        matrix, new_activities, activity, variants, total_dependencies
    ):
        raise ValueError("The input is invalid.")

    temporal_deps: Dict[Tuple[str, str], TemporalDependency] = {}
    existential_deps: Dict[Tuple[str, str], ExistentialDependency] = {}

    for (source, target), (temp_dep, exist_dep) in dependencies.items():
        if temp_dep:
            temporal_deps[(source, target)] = temp_dep
        if exist_dep:
            existential_deps[(source, target)] = exist_dep

    new_variants = []

    if satisfies_existential_constraints(
        set(activity), new_activities, existential_deps
    ):
        new_variants.append([activity])

    for variant in variants:
        if satisfies_existential_constraints(
            set(variant), new_activities, existential_deps
        ):
            new_variants.append(variant)
        variant_with_activity = variant.copy()
        variant_with_activity.append(activity)
        if not satisfies_existential_constraints(
            set(variant_with_activity), new_activities, existential_deps
        ):
            continue
        valid_variants = search_valid_positions_to_insert(
            variant, activity, temporal_deps
        )
        new_variants.extend(valid_variants)

    new_matrix = traces_to_adjacency_matrix(new_variants)

    return new_matrix