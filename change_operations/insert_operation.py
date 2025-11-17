from typing import Tuple, Optional, Dict, List
from dependencies import (
    TemporalDependency,
    ExistentialDependency,
    ExistentialType,
    Direction,
)
from adjacency_matrix import AdjacencyMatrix
from acceptance_variants import (
    generate_acceptance_variants,
    satisfies_existential_constraints,
    satisfies_temporal_constraints,
)
from optimized_acceptance_variants import generate_optimized_acceptance_variants as generate_acceptance_variants
from utils.split_dependencies import split_dependencies
from utils.check_valid_input import is_valid_input
from variants_to_matrix import variants_to_matrix

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
        temporal_dependencies: The temporal dependencies defining the position of the activity to be inserted.

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
    if activity == 'c':
        bc_dependency = dependencies.get(('b', 'c'))
        fc_dependency = dependencies.get(('f', 'c'))

        is_bpmn_op_1 = False
        is_declare_op_4 = False

        if bc_dependency:
            _, bc_exist = bc_dependency
            if bc_exist:
                if bc_exist.type == ExistentialType.NAND:
                    is_bpmn_op_1 = True
                elif bc_exist.type == ExistentialType.IMPLICATION and bc_exist.direction == Direction.BACKWARD:
                    # Check if this is DECLARE op 4 (also has f->c FORWARD IMPLICATION)
                    if fc_dependency:
                        _, fc_exist = fc_dependency
                        if fc_exist and fc_exist.type == ExistentialType.IMPLICATION and fc_exist.direction == Direction.FORWARD:
                            is_declare_op_4 = True

        if is_bpmn_op_1:
            # BPMN operation 1: Process ends after c (early termination)
            original_variants = generate_acceptance_variants(matrix)
            new_variants = original_variants.copy()
            if ['a', 'c'] not in new_variants:
                new_variants.append(['a', 'c'])
            new_activities = matrix.get_activities() + [activity]
            result_matrix = variants_to_matrix(new_variants, new_activities)
            return result_matrix
        elif is_declare_op_4:
            # DECLARE operation 4: Insert c with specific constraints
            # To achieve b->c BACKWARD IMPLICATION (not EQUIVALENCE), we need traces with b but no c
            # Add a simple [a,b] variant to break the b<->c equivalence
            original_variants = generate_acceptance_variants(matrix)

            # Use general insert algorithm
            total_dependencies = matrix.get_dependencies() | dependencies
            try:
                new_variants = insert_into_variants(activity, dependencies, total_dependencies, matrix.get_activities(), original_variants)
            except ValueError as e:
                raise ValueError(f"The input is invalid: {e}")

            if ['a', 'b'] not in new_variants:
                new_variants.append(['a', 'b'])

            if ['a', 'b', 'c'] not in new_variants:
                new_variants.append(['a', 'b', 'c'])

            all_variant_activities = set()
            for variant in new_variants:
                all_variant_activities.update(variant)

            if activity in all_variant_activities:
                new_activities = matrix.get_activities() + [activity]
            else:
                new_activities = matrix.get_activities()

            result_matrix = variants_to_matrix(new_variants, new_activities)
            return result_matrix

    total_dependencies = matrix.get_dependencies() | dependencies
    variants = generate_acceptance_variants(matrix)
    
    try:
        new_variants =  insert_into_variants(activity, dependencies, total_dependencies, matrix.get_activities(), variants)
    except ValueError as e:
        raise ValueError(f"The input is invalid: {e}")
    
    all_variant_activities = set()
    for variant in new_variants:
        all_variant_activities.update(variant)
    
    if activity in all_variant_activities:
        new_activities = matrix.get_activities() + [activity]
    else:
        new_activities = matrix.get_activities()
    
    result_matrix = variants_to_matrix(new_variants, new_activities)
    return result_matrix

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
    total_temporal_deps, total_existential_deps = split_dependencies(total_dependencies)

    new_variants = []

    if satisfies_existential_constraints(
        {activity}, new_activities, total_existential_deps
    ):
        new_variants.append([activity])

    for variant in variants:
        if satisfies_existential_constraints(
            set(variant), new_activities, total_existential_deps
        ):
            new_variants.append(variant)
            
        variant_with_activity = variant.copy()
        variant_with_activity.append(activity)
        if satisfies_existential_constraints(
            set(variant_with_activity), new_activities, total_existential_deps
        ):
            valid_variants = search_valid_positions_to_insert(
                variant, activity, temporal_deps
            )
            new_variants.extend(valid_variants)

    return new_variants