from typing import List, Set
from adjacency_matrix import AdjacencyMatrix
from acceptance_variants import generate_acceptance_variants
from traces_to_matrix import traces_to_adjacency_matrix
from dependencies import ExistentialType
from typing import Dict, Tuple, List, Optional
from dependencies import (
    TemporalDependency,
    ExistentialDependency,
    TemporalType,
    ExistentialType,
)

def add_dependency(
        matrix: AdjacencyMatrix ,
        from_activity: str,
        to_activity: str,
        temporal_dep: Optional[TemporalDependency],
        existential_dep: Optional[ExistentialDependency],
    ) -> AdjacencyMatrix: 
    """
    Modify a depenecy with activities which are part of the process: 
    1. Check that activities from_activity and to_activity are part of activities 
    2. Search or dependency and change the old dependency to the new activity 
    
    Args:
        matrix: The input adjacency matrix
        from_activity: The name of the activity from which the depenency is seen 
        to_activity: The name of the activity to which the dependency is seen 
        exist_dependency: Existential dependency which should become the new one 
        
    Returns:
        A new adjacency matrix with the adapted dependency 
        
    Raises:
        ValueError: If from_activity not found 
        ValueError: If to_activity not found
    """

    # modify the name of the activity to be replaced by the newly named activity  
    activities = matrix.get_activities
    dependencies = matrix.get_dependencies

    # check that activities are actually part of the matrix 
    if from_activity not in activities:
        raise ValueError(f"Activity {from_activity} not found in matrix")
    
    if to_activity not in activities:
        raise ValueError(f"Activity {to_activity} not found in matrix")
    

    # here we must consider the order in which the implication currently is cause the change operation needs to be adapted accoridngly 
    # replace in dict with dependencies 
    new_matrix = AdjacencyMatrix(activities) 
    new_dependencies = {}
    for (from_act, to_act), (temporal_dependency, existential_dependency) in dependencies.items():
        # way as also written in method call - no inversion of the dependency needed 
        if from_act == from_activity and to_act == to_activity: 
            if existential_dep: 
                existential_dependency = existential_dep
            if temporal_dep:
                temporal_dependency = temporal_dep
        # inverse to the way written in the function call - inversion needed 
        elif from_act == to_activity and to_act == from_activity: 
            # TODO must be inversed for new existential dependency 
            if existential_dep: 
                existential_dependency = existential_dep
            if temporal_dep:
                temporal_dependency = temporal_dep

        new_matrix.add_dependency(from_act, to_act, temporal_dependency, existential_dependency)

    return new_matrix
