from typing import List, Set, Dict, Tuple
from adjacency_matrix import AdjacencyMatrix
from acceptance_variants import generate_acceptance_variants
from traces_to_matrix import traces_to_adjacency_matrix
from dependencies import ExistentialType


def locked_dependencies_preserved(initial_matrix: AdjacencyMatrix, modified_matrix: AdjacencyMatrix, locked_dependencies: Dict[Tuple[str, str], Tuple[bool, bool]], deletion_allowed: bool) -> bool:
    """
    Check if provided constraints are fullfilled, meaning that depencies which are locked are not modified when applying the change operation 
    
    Args:
        initial_matrix: The adjacency matrix before performing the change operation
        modified_matrix: The adjacency matrix after performing the change operation
        locked_dependencies: List of deoendnecies which are locked (activity1, activity2, depenency_type) which should be esnured. The first tuples describes the activities and the second one (temporal, depency) 
        describes which of the depencies are locked  
        deletion_allowed: Indicates if the deletion of the depenedency by deleting one of the activities is allowed (if set to true, and A is deleted the locked dependency A to B, still is valid)
        
    Returns:
        Boolean value, depending on, if the check passes. If the dependencies are preserved, return true, else return false
        
    """
    initial_dependencies = initial_matrix.get_dependencies()
    modified_dependencies = modified_matrix.get_dependencies()

    # if the deletion is allowed, we only check for all the activities which are in the modified matrix, if dependencies were removed, they are not checked 
    if deletion_allowed:
        for (source, target) in modified_dependencies: 
            # check if the current tuple of activities is a locked dependency 
            # TODO also check for the other direction (target, source) that it holds, can be done if the directions are implemented 
            if (source, target) in locked_dependencies:
                # get the modified dependency and compare it to the initial one 
                (modi_temp_dep, modi_exist_dep) = modified_dependencies.get((source, target))
                (temporal_dependency, existential_dependency) = initial_dependencies.get((source, target))

                # get for which dependencies we must check 
                (temp_locked, exist_locked) = locked_dependencies.get((source, target))

                # check if temporal dependnecy is locked, if it remained 
                if temp_locked: 
                    print(modi_temp_dep, temporal_dependency)
                    if modi_temp_dep != temporal_dependency: 
                        return False
                    
                # check if existential dependnecy is locked, if it remained 
                if exist_locked: 
                    if modi_exist_dep != existential_dependency: 
                        return False

        # if all of the checks pass and the modified matrix fullfills the given conditions
        return True

    # check in case that deletion is not allowed of the locked dependencies    
    else: 
        for (source, target) in locked_dependencies: 
            # check that the activities required for the dependnecies are actually still in the matrix 
            if source not in modified_matrix.get_activities() or target not in modified_matrix.get_activities(): 
                # return false in case that some of the activities of locked dependencies are missing
                return False
            
        # check like above tht the criterias are met 
        for (source, target) in modified_dependencies: 
            # check if the current tuple of activities is a locked dependency 
            # TODO also check for the other direction (target, source) that it holds, can be done if the directions are implemented 
            if (source, target) in locked_dependencies:
                # get the modified dependency and compare it to the initial one 
                (modi_temp_dep, modi_exist_dep) = modified_matrix.get_dependency(source, target)
                (temporal_dependency, existential_dependency) = initial_dependencies.get((source, target))

                # get for which dependencies we must check 
                (temp_locked, exist_locked) = locked_dependencies.get((source, target))

                # check if temporal dependnecy is locked, if it remained 
                if temp_locked: 
                    print(modi_temp_dep, temporal_dependency)
                    if modi_temp_dep != temporal_dependency: 
                        return False
                    
                # check if existential dependnecy is locked, if it remained 
                if exist_locked: 
                    if modi_exist_dep != existential_dependency: 
                        return False

        # if all of the checks pass and the modified matrix fullfills the given conditions
        return True

def get_violated_locked_dependencies(
    initial_matrix: AdjacencyMatrix,
    modified_matrix: AdjacencyMatrix,
    locked_dependencies: Dict[Tuple[str, str], Tuple[bool, bool]],
    deletion_allowed: bool
) -> Dict[Tuple[str, str], Tuple[bool, bool]]:
    """
    Returns a dictionary of violated locked dependencies, indicating whether the temporal and/or existential 
    constraint was violated for each dependency.

    Args:
        initial_matrix: The adjacency matrix before performing the change operation.
        modified_matrix: The adjacency matrix after performing the change operation.
        locked_dependencies: Dictionary where key is (source, target) and value is (temporal_locked, existential_locked).
        deletion_allowed: If true, deletion of a dependency due to deletion of an activity is allowed.

    Returns:
        A dictionary mapping (source, target) to a tuple (temporal_violated, existential_violated). It so indictaes which dependencies were violated
    """
    violations: Dict[Tuple[str, str], Tuple[bool, bool]] = {}
    initial_dependencies = initial_matrix.get_dependencies()
    modified_dependencies = modified_matrix.get_dependencies()


    for (source, target), (temp_locked, exist_locked) in locked_dependencies.items():
        temporal_violated = False
        existential_violated = False

        # Handle deletion case
        if not deletion_allowed:
            if source not in modified_matrix.get_activities() or target not in modified_matrix.get_activities():
                if temp_locked:
                    temporal_violated = True
                if exist_locked:
                    existential_violated = True
                violations[(source, target)] = (temporal_violated, existential_violated)

        # Otherwise, check if the locked parts changed
        modi_temp_dep, modi_exist_dep = modified_matrix.get_dependency(source, target)
        temporal_dependency, existential_dependency = initial_dependencies.get((source, target), (None, None))

        if temp_locked and modi_temp_dep != temporal_dependency:
            temporal_violated = True
        if exist_locked and modi_exist_dep != existential_dependency:
            existential_violated = True

        if temporal_violated or existential_violated:
            violations[(source, target)] = (temporal_violated, existential_violated)

    return violations  