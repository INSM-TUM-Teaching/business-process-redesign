from typing import List, Set, Dict, Tuple
from adjacency_matrix import AdjacencyMatrix
from acceptance_variants import generate_acceptance_variants
from traces_to_matrix import traces_to_adjacency_matrix
from dependencies import ExistentialType


def locked_dependencies_preserved(initial_matrix: AdjacencyMatrix, modified_matrix: AdjacencyMatrix, locked_dependencies: Dict[Tuple[str, str], Tuple[bool, bool]]) -> bool:
    """
    Check if provided constraints are fullfilled, meaning that depencies which are locked are not modified when applying the change operation 
    
    Args:
        initial_matrix: The adjacency matrix before performing the change operation
        modified_matrix: The adjacency matrix after performing the change operation
        locked_dependencies: List of deoendnecies which are locked (activity1, activity2, depenency_type) which should be esnured. The first tuples describes the activities and the second one (temporal, depency) 
        describes which of the depencies are locked  
        
    Returns:
        Boolean value, depending on, if the check passes. If the dependencies are preserved, return true, else return false
        
    """
    initial_dependencies = initial_matrix.get_dependencies()

    for (source, target) in initial_dependencies: 
        # check if the current tuple of activities is a locked dependency 
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