from typing import List, Set, Tuple, Dict, Optional
from itertools import permutations
from acceptance_variants import generate_acceptance_variants
from adjacency_matrix import AdjacencyMatrix
from dependencies import TemporalType, TemporalDependency, ExistentialDependency
from traces_to_matrix import traces_to_adjacency_matrix

def get_unique_elements_between_parallel_activities(variants: List[List[str]], parallel_activities: Set[str]) -> List[str]:
    """
    Extracts all unique elements that occur between any two parallelized activities across multiple variants.
    
    Args:
        variants: A list of variants, each being a list of activity names.
        parallelize_activities: A set of activity names considered for parallelizing.
        
    Returns:
        A list of unique activity names that are strictly between two consecutive parallelize activities.
    """
    elements_in_between = []

    for variant in variants:
        # Find indexes of collapse activities in this variant
        parallel_indexes = [i for i, activity in enumerate(variant) if activity in parallel_activities]
        parallel_indexes.sort()
        
        for i in range(len(parallel_indexes) - 1):
            start = parallel_indexes[i]
            end = parallel_indexes[i + 1]
            # Add elements between start and end
            for elem in variant[start + 1:end]:
                if elem not in parallel_activities and elem not in elements_in_between:
                    elements_in_between.append(elem)
    
    return elements_in_between

def check_valid_input(
        dependencies: Dict[
            Tuple[str, str],
            Tuple[Optional[TemporalDependency], Optional[ExistentialDependency]],
        ], 
        variants: List[List[str]], parallel_activities: List[str]
    ) -> bool:
    """
    Define set X = {x1, x2, …, xn} to be parallelized
    Create all variants 
    Check for all variants if there exists a y with y ∉ X with x1 < y < x2
    If there is no such y existing: parallelize  
    Else: check if y is temporally independent to x1 , x2
        If this is case: parallelize  
        Else: reject 
    """
    # Check for existing activities y, which are in variants between elements of parallelize_activities 
    activities_in_between = get_unique_elements_between_parallel_activities(variants, parallel_activities)

    if not activities_in_between:
        # if activities in between are empty, we can directly paralellize
        return True
    
    else: 
        for activity in activities_in_between:
            for parallel_activity in parallel_activities:
                # ensure that the y which happens in between is temporally independent to all of the elements of the activities to be parallelized
                temporal_dep, _ = dependencies.get(activity, parallel_activity)
                # check for dependency type 
                if temporal_dep.type != TemporalType.INDEPENDENCE:
                    # then parallelizing not possible, problem is that we have activities happening in between
                    return False
    return True

def parallelize_activities_on_variants(
        parallel_activities: Set[str], 
        dependencies: Dict[
            Tuple[str, str],
            Tuple[Optional[TemporalDependency], Optional[ExistentialDependency]],
        ], 
        variants: List[List[str]]) -> List[List[str]]:
    """
    Parallelizes activities by:
    1. Checking if input is valid
    2. Creating permutations of parallel_activities
    3. Past all permutations in variants for first activity in parallel_activites to be found and delete all other activites in parallel activities from variant

    Args:
        parallell_activities: The name of the activities to be paralellized
        dependencies: Depenedencies between the activities.
        variants: The variants in which the activites should be parallelized

    Returns:
       The new variants with the activities parallelized

    Raises:
        ValueError: If input produces contradiction
    """

    if not check_valid_input(dependencies, variants, parallel_activities):
        raise ValueError("Invalid input")
    
    perms = [list(p) for p in permutations(parallel_activities, len(parallel_activities))]
    new_variants = []

    for variant in variants:
        pos = 0
        for activity in parallel_activities:
            if activity in variant:
                pos = variant.index(activity)
                variant.remove(activity)
        for permutation in perms:
            new_variant = variant.copy()
            for activity in permutation:
                new_variant.insert(pos, activity)
            new_variants.append(new_variant.copy())

    return new_variants



def parallelize_activities(matrix: AdjacencyMatrix, parallel_activities: Set[str]):
    """
    Parallelizes activities in matrix:
    1. Generating variants for the input matrix.
    2. Parallelize in variants.
    3. Convert variants to new matrix.

    Args:
        matrix: The input adjacency matrix
        parallell_activities: The name of the activities to be paralellized

    Returns:
        A new adjacency matrix with the activities parallelized

    Raises:
        ValueError: If input produces contradiction
    """
    variants = generate_acceptance_variants(matrix)

    try:
        new_variants = parallelize_activities_on_variants(parallel_activities, matrix.dependencies, variants)
    except ValueError as e:
        raise ValueError({e}) from e
    
    new_matrix = traces_to_adjacency_matrix(new_variants)
    
    return new_matrix