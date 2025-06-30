from typing import List, Set
from itertools import permutations
from acceptance_variants import generate_acceptance_variants, build_permutations
from adjacency_matrix import AdjacencyMatrix
from dependencies import TemporalType
from traces_to_matrix import traces_to_adjacency_matrix

def get_unique_elements_between_parallel_activities(variants: List[List[str]], parallel_activities: Set[str]) -> List[str]:
    """
    Extracts all unique elements that occur between any two collapse activities across multiple variants.
    
    Args:
        variants: A list of variants, each being a list of activity names.
        collapse_activities: A set of activity names considered for collapsing.
        
    Returns:
        A list of unique activity names that are strictly between two consecutive collapse activities.
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

def check_valid_input(matrix: AdjacencyMatrix, variants: List[List[str]], parallel_activities: List[str]):
    """
    Define set X = {x1, x2, …, xn} to be parallelized
    Create all variants 
    Check for all variants if there exists a y with y ∉ X with x1 < y < x2
    If there is no such y existing: parallelize  
    Else: check if y is temporally independent to x1 , x2
        If this is case: parallelize  
        Else: reject 
    """
    # Check for existing activities y, which are in variants between elements of collapse_activities 
    activities_in_between = get_unique_elements_between_parallel_activities(variants, parallel_activities)

    if not activities_in_between:
        # if activities in between are empty, we can directly collapse 
        return True
    
    else: 
        for activity in activities_in_between:
            for collapse_activity in parallel_activities:
                # ensure that the y which happens in between is temporally independnet to all of the elements of the activities to be collapsed 
                temporal_dep, existential_dep = matrix.get_dependency(activity, collapse_activity)
                # check for dependency type 
                if temporal_dep.type != TemporalType.INDEPENDENCE:
                    # then collapsing not possible, problem is that we have activities happening in between 
                    return False
    return True

def parallelize_activities(matrix: AdjacencyMatrix, parallel_activities: Set[str]):
    """
    Parallelize activities
    """
    variants = generate_acceptance_variants(matrix)

    if not check_valid_input(matrix, variants, parallel_activities):
        raise ValueError("Invalid input")
    
    perms = [list(p) for p in permutations(parallel_activities, len(parallel_activities))]
    print(perms)
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

    print(new_variants)
    
    new_matrix = traces_to_adjacency_matrix(new_variants)
    
    return new_matrix