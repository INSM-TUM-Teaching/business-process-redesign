import pytest
from dependencies import TemporalDependency, TemporalType, ExistentialDependency, ExistentialType
from adjacency_matrix import AdjacencyMatrix
from change_operations.parallelize_operation import parallelize_activities, parallelize_activities_on_variants

def test_parallelize_variants():
    variants = [["A", "B"]]
    dependencies = {
        ("A", "B"):
        (TemporalDependency(TemporalType.DIRECT), ExistentialDependency(ExistentialType.EQUIVALENCE))
        }

    expected = [["A", "B"], ["B", "A"]]
    actual = parallelize_activities_on_variants(set(["A", "B"]), dependencies, variants)

    # Sort inner lists and then sort the outer list
    expected_sorted = sorted(expected)
    actual_sorted = sorted(actual)

    seen = set()
    actual_sorted_without_duplicates = []
    for inner in actual_sorted:
        tuple_inner = tuple(inner)
        if tuple_inner not in seen:
            seen.add(tuple_inner)
            actual_sorted_without_duplicates.append(inner)

    assert expected_sorted == actual_sorted_without_duplicates

    variants = [["A", "B", "C"], ["A", "C"]]
    dependencies = {
        ("A", "B"):
        (TemporalDependency(TemporalType.DIRECT), ExistentialDependency(ExistentialType.IMPLICATION)), # imp backward
        ("A", "C"):
        (TemporalDependency(TemporalType.EVENTUAL), ExistentialDependency(ExistentialType.EQUIVALENCE)),
        ("B", "C"):
        (TemporalDependency(TemporalType.DIRECT), ExistentialDependency(ExistentialType.IMPLICATION))
    }

    expected = [["A", "B", "C"], ["A", "C", "B"], ["B", "A", "C"], ["B", "C", "A"], ["C","A","B"],["C","B","A"]]
    actual = parallelize_activities_on_variants(set(["A", "B", "C"]), dependencies, variants)

    # Sort inner lists and then sort the outer list
    expected_sorted = sorted(expected)
    actual_sorted = sorted(actual)

    # remove dublicates
    seen = set()
    actual_sorted_without_duplicates = []
    for inner in actual_sorted:
        tuple_inner = tuple(inner)
        if tuple_inner not in seen:
            seen.add(tuple_inner)
            actual_sorted_without_duplicates.append(inner)

    assert expected_sorted == actual_sorted_without_duplicates

def test_parallelize_invalid_input():
    variants = [[]]
    dependencies = dict()

    with pytest.raises(Exception):
        parallelize_activities_on_variants(set(["A", "B"]), dependencies, variants)
    
    variants = [["A", "B", "C"], ["A", "C"]]
    dependencies = {
        ("A", "B"):
        (TemporalDependency(TemporalType.DIRECT), ExistentialDependency(ExistentialType.IMPLICATION)), # imp backward
        ("A", "C"):
        (TemporalDependency(TemporalType.EVENTUAL), ExistentialDependency(ExistentialType.EQUIVALENCE)),
        ("B", "C"):
        (TemporalDependency(TemporalType.DIRECT), ExistentialDependency(ExistentialType.IMPLICATION))
    }

    with pytest.raises(Exception):
        parallelize_activities_on_variants(set(["A", "C"]), dependencies, variants)

def test_parallelize_activities():
    matrix = AdjacencyMatrix(activities=["A", "B"])
    matrix.add_dependency(
        "A", "B",
        TemporalDependency(TemporalType.DIRECT),
        ExistentialDependency(ExistentialType.EQUIVALENCE)
    )
    result_matrix = AdjacencyMatrix(activities=["A", "B"])
    result_matrix.add_dependency(
        "A", "B",
        None,
        ExistentialDependency(ExistentialType.EQUIVALENCE)
    )
    result_matrix.add_dependency(
        "B", "A",
        None,
        ExistentialDependency(ExistentialType.EQUIVALENCE)
    )

    assert parallelize_activities(matrix, set(["A", "B"])) == result_matrix