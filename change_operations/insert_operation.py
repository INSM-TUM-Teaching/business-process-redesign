from typing import Tuple, Optional, Dict, List, Set
from z3 import Solver, Bool, Implies, Xor, Not, And, Or, sat
from dependencies import (
    TemporalDependency,
    ExistentialDependency,
    TemporalType,
    ExistentialType,
    Direction,
)
from adjacency_matrix import AdjacencyMatrix
from acceptance_variants import (
    generate_acceptance_variants,
    satisfies_existential_constraints,
    satisfies_temporal_constraints,
)
from traces_to_matrix import traces_to_adjacency_matrix

def split_dependencies(
    dependencies: Dict[
        Tuple[str, str],
        Tuple[Optional[TemporalDependency], Optional[ExistentialDependency]],
    ]
) -> Tuple[
    Dict[Tuple[str, str], TemporalDependency],
    Dict[Tuple[str, str], ExistentialDependency],
]:
    """
    Splits a dictionary of combined dependencies into separate dictionaries
    for temporal and existential dependencies.

    Args:
        dependencies: Dictionary with (temporal, existential) dependency tuples.

    Returns:
        A tuple with two dictionaries: (temporal_dependencies, existential_dependencies)
    """
    temporal_deps: Dict[Tuple[str, str], TemporalDependency] = {}
    existential_deps: Dict[Tuple[str, str], ExistentialDependency] = {}

    for (source, target), (temp_dep, exist_dep) in dependencies.items():
        if temp_dep:
            temporal_deps[(source, target)] = temp_dep
        if exist_dep:
            existential_deps[(source, target)] = exist_dep

    return temporal_deps, existential_deps

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

    activity_names = set()
    for a, b in existential_deps.keys():
        activity_names.update([a, b])

    for name in activity_names:
        variables[name] = Bool(name)

    for (a, b), dep in existential_deps.items():
        var_a = variables[a]
        var_b = variables[b]

        # Handle case where dep might be a tuple (temporal, existential)
        if isinstance(dep, tuple):
            dep = dep[1]  # Extract existential dependency from tuple
        
        if dep is None:
            continue

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
            constraint = True

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
    # Convert dependencies to a normalized form to avoid processing redundant constraints
    normalized_deps = {}
    for (source, target), dep in temporal_deps.items():
        if dep.type == TemporalType.INDEPENDENCE:
            continue
        
        # Determine the actual direction based on the dependency direction
        if dep.direction == Direction.FORWARD:
            # source comes before target
            before, after = source, target
        elif dep.direction == Direction.BACKWARD:
            # source comes after target (so target comes before source)
            before, after = target, source
        else:  # Direction.BOTH - skip for cycle detection
            continue
        
        # Normalize to always have the "before" activity as the key
        # This avoids processing the same constraint twice
        constraint_key = (before, after)
        if constraint_key not in normalized_deps:
            normalized_deps[constraint_key] = dep
    
    # Now process the normalized dependencies
    for (before, after), dep in normalized_deps.items():
        if after == cur_activity:
            if before in visited:
                raise RecursionError(f"Temporal contradiction: cycle detected between '{before}' and '{cur_activity}'")
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
    after = set()
    before = set()
    for source, target in temporal_deps:
        dep = temporal_deps.get((source, target))
        if dep.type != TemporalType.DIRECT:
            continue
        
        # Determine actual order based on direction
        if dep.direction == Direction.FORWARD:
            # source comes before target
            actual_before, actual_after = source, target
        elif dep.direction == Direction.BACKWARD:
            # target comes before source (source comes after target)
            actual_before, actual_after = target, source
        else:  # Direction.BOTH - skip for contradiction checking
            continue
            
        if actual_after == activity:
            before.add(actual_before)
        if actual_before == activity:
            after.add(actual_after)

    for variant in variants:
        variant_activities = set(variant)
        variant_activities.add(activity)
        if not satisfies_existential_constraints(variant_activities, activities, existential_deps):
            continue

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

    try:
        for a in activities:
            dfs(temporal_deps, a, set())
    except RecursionError as e:
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
    temporal_deps, existential_deps = split_dependencies(total_dependencies)

    if activity in activities:
        raise ValueError(f"The activity '{activity}' is already present in the matrix.")
    if has_existential_contradiction(existential_deps):
        raise ValueError("Existential dependencies cause a contradiction.")
    if has_temporal_contradiction(temporal_deps, existential_deps, new_activities, activity, variants):
        raise ValueError("Temporal dependencies cause a contradiction.")
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
    except ValueError as e:
        raise ValueError(f"The input is invalid: {e}")
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

    try:
        is_valid_input(activities, new_activities, activity, variants, total_dependencies)
    except ValueError as e:
        raise ValueError(str(e)) from e

    temporal_deps, existential_deps = split_dependencies(dependencies)

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
