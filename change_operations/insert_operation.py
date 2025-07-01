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
    Checks if there is a contradiction in the existential dependencies.

    Args:
        existential_deps: The existential dependencies for which the check should be performed

    Returns:
        True, if it has a contradiction
        False, if there is no contradiction
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
        else:
            constraint = True  # Independence

        solver.add(constraint)

    result = solver.check()
    return not (result == sat)


def dfs(
    temporal_deps: Dict[Tuple[str, str], TemporalDependency],
    cur_activity: str,
    visited: Set[str]
):
    """
    Depth first search recursively checking if there are loops in temporal dependencies.

    Args:
        temporal_deps: The temporal dependencies among the activities where there
        cur_activity: The activity to perform the next step for
        visited: Set of activities which have already been visited
    
    Returns:
        The set of activities which have been visited.

    Raises:
        RecursionError if there is a loop.
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
    existential_deps: Dict[Tuple[str, str], ExistentialDependency],
    activities: List[str],
    activity: str,
    variants: List[List[str]],
):
    """
    Checks if there is a contradiction in the temporal dependencies.

    Args:
        temporal_deps: The temporal deps for which the check should be performed.
        existential_deps: The existential dependencies belonging to the temporal_deps.
        activities: List of all activities.
        activity: List of activity to be inserted
        variants: Variants of the matrix for which the check should be performed.

    Returns:
        True, if it has a contradiction
        False, if there is no contradiction
    """

    # Get sets of activities directly before and after
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
        variant_activities = set(variant)
        variant_activities.add(activity)
        if satisfies_existential_constraints(variant_activities, activities, existential_deps):
            continue

        # check if there is max 1 before and max 1 after in each variant
        # check if with a direct before and after if there is something in between, then there is a contradiction.
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
            if (a_pos != (b_pos + 1)):
                return True
    # Check for loops
    try:
        for a in activities:
            dfs(temporal_deps, a, set())
    except RecursionError:
        return True

    return False


def is_valid_input(
    activities,
    new_activities,
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
        activities: All activities from orignial matrix.
        new_activites: All activities from orignial matrix and activity to be inserted.
        activity: The name of the activity to insert.
        variants: All variants reslting from matrix.
        total_dependencies: The dependencies defining the position of the activity to be inserted.

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

    if activity in activities:
        return False
    if has_existential_contradiction(total_existential_deps):
        return False
    if has_temporal_contradiction(total_temporal_deps, total_existential_deps, new_activities, activity, variants):
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
    1. Generating variants for the input matrix.
    2. Insert into variants.
    3. Convet variants to new matrix.

    Args:
        matrix: The input adjacency matrix
        activity: The name of the activity to insert
        dependencies: The dependencies defining the position of the activity to be inserted

    Returns:
        A new adjacency matrix with the activity inserted

    Raises:
        ValueError: If input produces contradiction
    """
    total_dependencies = matrix.get_dependencies() | dependencies
    variants = generate_acceptance_variants(matrix)
    try:
        new_variants =  insert_into_variants(activity, dependencies, total_dependencies, matrix.get_activities(), variants)
    except:
        raise ValueError("The input is invalid")
    return traces_to_adjacency_matrix(new_variants)



def insert_into_variants(
    activity: str,
    dependencies: Dict[
        Tuple[str, str],
        Tuple[Optional[TemporalDependency], Optional[ExistentialDependency]],
    ],
    total_dependencies: Dict[
        Tuple[str, str],
        Tuple[Optional[TemporalDependency], Optional[ExistentialDependency]],
    ],
    activities: List[str],
    variants: List[List[str]]
    )-> List[List[str]]:
    """
    Adds a new acivity to the process by:
    1. Checking if input is valid.
    2. Checking if for variant existential dependencies hold with and without activity to be inserted.
    3. Inserting according to direct or eventual temporal dependencies.

    Args:
        activity: The name of the activity to insert
        dependencies: The dependencies defining the position of the activity to be inserted
        total_dependencies: Dependencies which also include all the dependencies from the original matrix
        activities: The activities from the original matrix
        variants: Variants of the original matrix

    Returns:
        Variants of the process with activity inserted.

    Raises:
        ValueError: If input produces contradiction
    """

    new_activities = activities.copy()
    new_activities.append(activity)

    if not is_valid_input(
        activities, new_activities, activity, variants, total_dependencies
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

    return new_variants