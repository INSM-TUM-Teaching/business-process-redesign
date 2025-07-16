from typing import Tuple, Dict, List, Set
from z3 import Solver, Bool, Implies, Xor, Not, And, Or, sat
from dependencies import (
    TemporalDependency,
    ExistentialDependency,
    TemporalType,
    ExistentialType,
    Direction,
)
from acceptance_variants import (
    satisfies_existential_constraints,
)

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

def _dfs(
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
            visited = visited | _dfs(temporal_deps, before, visited)
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
            _dfs(temporal_deps, a, set())
    except RecursionError:
        return True

    return False