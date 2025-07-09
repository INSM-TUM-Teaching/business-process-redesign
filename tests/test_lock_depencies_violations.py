import pytest
from typing import List, Set, Dict, Tuple
from adjacency_matrix import AdjacencyMatrix
from dependencies import (
    TemporalDependency,
    ExistentialDependency,
    TemporalType,
    ExistentialType,
    Direction
)
from utils.lock_dependencies_violations import locked_dependencies_preserved, get_violated_locked_dependencies


def test_locked_dependency_preserved_no_violations():  

    # Create a simple matrix with A < B < C dependencies
    matrix = AdjacencyMatrix(activities=["A", "B", "C"])
    
    # define the matrix with dependencies 
    matrix.add_dependency(
        "A", "B",
        TemporalDependency(TemporalType.DIRECT, Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    matrix.add_dependency(
        "A", "C",
        TemporalDependency(TemporalType.EVENTUAL, Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    matrix.add_dependency(
        "B", "A",
        TemporalDependency(TemporalType.DIRECT, Direction.BACKWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    matrix.add_dependency(
        "B", "C",
        TemporalDependency(TemporalType.DIRECT, Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    matrix.add_dependency(
        "C", "A",
        TemporalDependency(TemporalType.EVENTUAL, Direction.BACKWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    matrix.add_dependency(
        "C", "B",
        TemporalDependency(TemporalType.EVENTUAL, Direction.BACKWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )

    # create the modify matrix which we use to do changes accoridngly 
    modified_matrix = AdjacencyMatrix(activities=["A", "B", "C"])
    
    # define the matrix with dependencies 
    modified_matrix.add_dependency(
        "A", "B",
        TemporalDependency(TemporalType.DIRECT, Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    modified_matrix.add_dependency(
        "A", "C",
        TemporalDependency(TemporalType.EVENTUAL, Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    modified_matrix.add_dependency(
        "B", "A",
        TemporalDependency(TemporalType.DIRECT, Direction.BACKWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    modified_matrix.add_dependency(
        "B", "C",
        TemporalDependency(TemporalType.DIRECT, Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    modified_matrix.add_dependency(
        "C", "A",
        TemporalDependency(TemporalType.EVENTUAL, Direction.BACKWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    modified_matrix.add_dependency(
        "C", "B",
        TemporalDependency(TemporalType.EVENTUAL, Direction.BACKWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )

    # define the dependencies to be locked 
    locked_dependencies: Dict[Tuple[str, str], Tuple[bool, bool]] = {}
    locked_dependencies[("A", "B")] = (True, True)

    # perform the test whether the function returns the correct value - True in this case since no changes were performed 
    assert locked_dependencies_preserved(matrix, modified_matrix, locked_dependencies, (True, True)) == True


def test_locked_dependency_preserved_violations():  

    # Create a simple matrix with A < B < C dependencies
    matrix = AdjacencyMatrix(activities=["A", "B", "C"])
    
    # define the matrix with dependencies 
    matrix.add_dependency(
        "A", "B",
        TemporalDependency(TemporalType.DIRECT, Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    matrix.add_dependency(
        "A", "C",
        TemporalDependency(TemporalType.EVENTUAL, Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    matrix.add_dependency(
        "B", "A",
        TemporalDependency(TemporalType.DIRECT, Direction.BACKWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    matrix.add_dependency(
        "B", "C",
        TemporalDependency(TemporalType.DIRECT, Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    matrix.add_dependency(
        "C", "A",
        TemporalDependency(TemporalType.EVENTUAL, Direction.BACKWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    matrix.add_dependency(
        "C", "B",
        TemporalDependency(TemporalType.EVENTUAL, Direction.BACKWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )

    # create the modify matrix which we use to do changes accoridngly 
    modified_matrix = AdjacencyMatrix(activities=["A", "B", "C"])
    
    # define the matrix with dependencies 
    modified_matrix.add_dependency(
        "A", "B",
        TemporalDependency(TemporalType.EVENTUAL, Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    modified_matrix.add_dependency(
        "A", "C",
        TemporalDependency(TemporalType.EVENTUAL, Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    modified_matrix.add_dependency(
        "B", "A",
        TemporalDependency(TemporalType.DIRECT, Direction.BACKWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    modified_matrix.add_dependency(
        "B", "C",
        TemporalDependency(TemporalType.DIRECT, Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    modified_matrix.add_dependency(
        "C", "A",
        TemporalDependency(TemporalType.EVENTUAL, Direction.BACKWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    modified_matrix.add_dependency(
        "C", "B",
        TemporalDependency(TemporalType.EVENTUAL, Direction.BACKWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )

    # define the dependencies to be locked 
    locked_dependencies: Dict[Tuple[str, str], Tuple[bool, bool]] = {}
    locked_dependencies[("A", "B")] = (True, True)

    # perform the test whether the function returns the correct value - True in this case since no changes were performed 
    assert locked_dependencies_preserved(matrix, modified_matrix, locked_dependencies, (True, True)) == False


def test_locked_dependency_deletion_allowed():  

    # Create a simple matrix with A < B < C dependencies
    matrix = AdjacencyMatrix(activities=["A", "B", "C"])
    
    # define the matrix with dependencies 
    matrix.add_dependency(
        "A", "B",
        TemporalDependency(TemporalType.DIRECT, Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    matrix.add_dependency(
        "A", "C",
        TemporalDependency(TemporalType.EVENTUAL, Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    matrix.add_dependency(
        "B", "A",
        TemporalDependency(TemporalType.DIRECT, Direction.BACKWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    matrix.add_dependency(
        "B", "C",
        TemporalDependency(TemporalType.DIRECT, Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    matrix.add_dependency(
        "C", "A",
        TemporalDependency(TemporalType.EVENTUAL, Direction.BACKWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    matrix.add_dependency(
        "C", "B",
        TemporalDependency(TemporalType.EVENTUAL, Direction.BACKWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )

    # create the modify matrix which we use to do changes accoridngly 
    modified_matrix = AdjacencyMatrix(activities=["A", "B", "C"])
    
    # define the matrix with dependencies 
    modified_matrix.add_dependency(
        "A", "C",
        TemporalDependency(TemporalType.EVENTUAL, Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    modified_matrix.add_dependency(
        "B", "C",
        TemporalDependency(TemporalType.DIRECT, Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    modified_matrix.add_dependency(
        "C", "A",
        TemporalDependency(TemporalType.EVENTUAL, Direction.BACKWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    modified_matrix.add_dependency(
        "C", "B",
        TemporalDependency(TemporalType.EVENTUAL, Direction.BACKWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )

    # define the dependencies to be locked 
    locked_dependencies: Dict[Tuple[str, str], Tuple[bool, bool]] = {}
    locked_dependencies[("A", "B")] = (True, True)

    # perform the test whether the function returns the correct value - True in this case since no changes were performed 
    assert locked_dependencies_preserved(matrix, modified_matrix, locked_dependencies, (True, True)) == True


def test_get_violated_locked_dependencies():  

    # Create a simple matrix with A < B < C dependencies
    matrix = AdjacencyMatrix(activities=["A", "B", "C"])
    
    # define the matrix with dependencies 
    matrix.add_dependency(
        "A", "B",
        TemporalDependency(TemporalType.DIRECT, Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    matrix.add_dependency(
        "A", "C",
        TemporalDependency(TemporalType.EVENTUAL, Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    matrix.add_dependency(
        "B", "A",
        TemporalDependency(TemporalType.DIRECT, Direction.BACKWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    matrix.add_dependency(
        "B", "C",
        TemporalDependency(TemporalType.DIRECT, Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    matrix.add_dependency(
        "C", "A",
        TemporalDependency(TemporalType.EVENTUAL, Direction.BACKWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    matrix.add_dependency(
        "C", "B",
        TemporalDependency(TemporalType.EVENTUAL, Direction.BACKWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )

    # create the modify matrix which we use to do changes accoridngly 
    modified_matrix = AdjacencyMatrix(activities=["A", "B", "C"])
    
    # define the matrix with dependencies 
    modified_matrix.add_dependency(
        "A", "B",
        TemporalDependency(TemporalType.EVENTUAL, Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    modified_matrix.add_dependency(
        "A", "C",
        TemporalDependency(TemporalType.EVENTUAL, Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    modified_matrix.add_dependency(
        "B", "A",
        TemporalDependency(TemporalType.DIRECT, Direction.BACKWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    modified_matrix.add_dependency(
        "B", "C",
        TemporalDependency(TemporalType.DIRECT, Direction.FORWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    modified_matrix.add_dependency(
        "C", "A",
        TemporalDependency(TemporalType.EVENTUAL, Direction.BACKWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )
    modified_matrix.add_dependency(
        "C", "B",
        TemporalDependency(TemporalType.EVENTUAL, Direction.BACKWARD),
        ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)
    )

    # define the dependencies to be locked 
    locked_dependencies: Dict[Tuple[str, str], Tuple[bool, bool]] = {}
    locked_dependencies[("A", "B")] = (True, True)

    # define expected return value 
    violated_dependencies: Dict[Tuple[str, str], Tuple[bool, bool]] = {}
    violated_dependencies[("A", "B")] = (True, False)

    # perform the test whether the function returns the correct dependencies which were violated 
    assert get_violated_locked_dependencies(matrix, modified_matrix, locked_dependencies, (True, True)) == violated_dependencies