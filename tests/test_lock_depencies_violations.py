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
    assert locked_dependencies_preserved(matrix, modified_matrix, locked_dependencies, []) == True


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
    assert locked_dependencies_preserved(matrix, modified_matrix, locked_dependencies, []) == False


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
    assert locked_dependencies_preserved(matrix, modified_matrix, locked_dependencies, ["A", "B"]) == True


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
    assert get_violated_locked_dependencies(matrix, modified_matrix, locked_dependencies, []) == violated_dependencies

def test_temporal_only_lock_allows_deletion():
    """
    Test that temporal-only locks (True, False) allow deletion of activities,
    while existential locks (False, True) or both (True, True) prevent deletion.
    """
    # Create a matrix with A and B
    matrix = AdjacencyMatrix(activities=["A", "B", "C"])
    
    matrix.add_dependency(
        "A", "B",
        TemporalDependency(TemporalType.DIRECT, Direction.FORWARD),
        ExistentialDependency(ExistentialType.IMPLICATION, Direction.FORWARD)
    )
    
    # Modified matrix where A is deleted
    modified_matrix = AdjacencyMatrix(activities=["B", "C"])
    
    # Test 1: Temporal-only lock should ALLOW deletion
    locked_dependencies_temporal_only: Dict[Tuple[str, str], Tuple[bool, bool]] = {}
    locked_dependencies_temporal_only[("A", "B")] = (True, False)  # Only temporal locked
    
    assert locked_dependencies_preserved(matrix, modified_matrix, locked_dependencies_temporal_only, []) == True
    
    # Test 2: Existential-only lock should PREVENT deletion
    locked_dependencies_existential_only: Dict[Tuple[str, str], Tuple[bool, bool]] = {}
    locked_dependencies_existential_only[("A", "B")] = (False, True)  # Only existential locked
    
    assert locked_dependencies_preserved(matrix, modified_matrix, locked_dependencies_existential_only, []) == False
    
    # Test 3: Both locks should PREVENT deletion
    locked_dependencies_both: Dict[Tuple[str, str], Tuple[bool, bool]] = {}
    locked_dependencies_both[("A", "B")] = (True, True)  # Both locked
    
    assert locked_dependencies_preserved(matrix, modified_matrix, locked_dependencies_both, []) == False
    
    # Test 4: Temporal-only lock with deletion_allowed should also work
    assert locked_dependencies_preserved(matrix, modified_matrix, locked_dependencies_temporal_only, ["A"]) == True


def test_temporal_only_lock_deletion_violations():
    """
    Test that get_violated_locked_dependencies correctly reports violations
    for temporal-only locks when activities are deleted.
    """
    # Create a matrix with A and B
    matrix = AdjacencyMatrix(activities=["A", "B", "C"])
    
    matrix.add_dependency(
        "A", "B",
        TemporalDependency(TemporalType.DIRECT, Direction.FORWARD),
        ExistentialDependency(ExistentialType.IMPLICATION, Direction.FORWARD)
    )
    
    # Modified matrix where A is deleted
    modified_matrix = AdjacencyMatrix(activities=["B", "C"])
    
    # Test 1: Temporal-only lock should NOT report violations on deletion
    locked_dependencies_temporal_only: Dict[Tuple[str, str], Tuple[bool, bool]] = {}
    locked_dependencies_temporal_only[("A", "B")] = (True, False)
    
    violations = get_violated_locked_dependencies(matrix, modified_matrix, locked_dependencies_temporal_only, [])
    assert violations == {}  # No violations expected
    
    # Test 2: Existential-only lock should report existential violation on deletion
    locked_dependencies_existential_only: Dict[Tuple[str, str], Tuple[bool, bool]] = {}
    locked_dependencies_existential_only[("A", "B")] = (False, True)
    
    violations = get_violated_locked_dependencies(matrix, modified_matrix, locked_dependencies_existential_only, [])
    assert violations == {("A", "B"): (False, True)}  # Existential violation
    
    # Test 3: Both locks should report existential violation on deletion
    locked_dependencies_both: Dict[Tuple[str, str], Tuple[bool, bool]] = {}
    locked_dependencies_both[("A", "B")] = (True, True)
    
    violations = get_violated_locked_dependencies(matrix, modified_matrix, locked_dependencies_both, [])
    assert violations == {("A", "B"): (False, True)}  # Existential violation (temporal is ok since we allow deletion)
