import pytest
from adjacency_matrix import AdjacencyMatrix
from dependencies import (
    TemporalDependency,
    ExistentialDependency,
    TemporalType,
    ExistentialType,
)
from utils.lock_dependencies_1 import locked_dependencies_preserved


def test_dependency_preserved():
    # Create a simple matrix with A<->B dependencies
    initial_matrix = AdjacencyMatrix(activities=["A", "B"])
    
    initial_matrix.add_dependency(
        "A", "B",
        TemporalDependency(TemporalType.DIRECT),
        ExistentialDependency(ExistentialType.EQUIVALENCE)
    )
    initial_matrix.add_dependency(
        "B", "A",
        TemporalDependency(TemporalType.DIRECT),
        ExistentialDependency(ExistentialType.EQUIVALENCE)
    )

    # set the modified matrix equal to the initial matrix
    modified_matrix = initial_matrix

    # define the Dict for locked dependencies, from A to B we lock the temporal dependency 
    locked_dependencies = {
        ("A", "B"): (True, False)
    }
    
    # Check if locked dependencies are preserved 
    assert locked_dependencies_preserved(initial_matrix, modified_matrix, locked_dependencies) == True


def test_dependencies_changed():
    # Create a simple matrix with A<->B dependencies
    initial_matrix = AdjacencyMatrix(activities=["A", "B"])
    
    initial_matrix.add_dependency(
        "A", "B",
        TemporalDependency(TemporalType.DIRECT),
        ExistentialDependency(ExistentialType.EQUIVALENCE)
    )
    initial_matrix.add_dependency(
        "B", "A",
        TemporalDependency(TemporalType.DIRECT),
        ExistentialDependency(ExistentialType.EQUIVALENCE)
    )

    # set the modified matrix as an alternated one 
    modified_matrix = AdjacencyMatrix(activities=["A", "B"])
    
    modified_matrix.add_dependency(
        "A", "B",
        TemporalDependency(TemporalType.EVENTUAL),
        ExistentialDependency(ExistentialType.EQUIVALENCE)
    )
    modified_matrix.add_dependency(
        "B", "A",
        TemporalDependency(TemporalType.EVENTUAL),
        ExistentialDependency(ExistentialType.EQUIVALENCE)
    )

    # define the Dict for locked dependencies, from A to B we lock the temporal dependency 
    locked_dependencies = {
        ("A", "B"): (True, False)
    }
    
    # Check if locked dependencies are preserved 
    assert locked_dependencies_preserved(initial_matrix, modified_matrix, locked_dependencies) == False