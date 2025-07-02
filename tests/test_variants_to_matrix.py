import pytest
from variants_to_matrix import get_existential_relation_type, variants_to_matrix
from dependencies import ExistentialType, TemporalType
from adjacency_matrix import AdjacencyMatrix

def test_get_existential():
    variants = [["A", "B"], []]

    combinations = set(frozenset(variant) for variant in variants)

    assert get_existential_relation_type("A","B", combinations) == ExistentialType.EQUIVALENCE

    variants = [["A", "B"], ["B"]]

    combinations = set(frozenset(variant) for variant in variants)

    assert get_existential_relation_type("A","B", combinations) == ExistentialType.IMPLICATION

    variants = [["A", "B"], ["B"], ["A"]]

    combinations = set(frozenset(variant) for variant in variants)

    assert get_existential_relation_type("A","B", combinations) == ExistentialType.OR

    variants = [[], ["B"], ["A"]]

    combinations = set(frozenset(variant) for variant in variants)

    assert get_existential_relation_type("A","B", combinations) == ExistentialType.NAND

    variants = [["B"], ["A"]]

    combinations = set(frozenset(variant) for variant in variants)

    assert get_existential_relation_type("A","B", combinations) == ExistentialType.NEGATED_EQUIVALENCE

    variants = [["B"], ["A"], [], ["A", "B"]]

    combinations = set(frozenset(variant) for variant in variants)

    assert get_existential_relation_type("A","B", combinations) == ExistentialType.INDEPENDENCE

def test_variants_to_matrix():
    variants = [["A", "B", "C"],["A", "C", "B"]]

    matrix = variants_to_matrix(variants)

    assert matrix.activities == ["A", "B", "C"]

    temp_dep, exist_dep = matrix.get_dependency("B", "C")
    assert temp_dep.type == TemporalType.INDEPENDENCE
    assert exist_dep.type == ExistentialType.EQUIVALENCE

    temp_dep, exist_dep = matrix.get_dependency("A", "B")
    assert temp_dep.type == TemporalType.EVENTUAL
    assert exist_dep.type == ExistentialType.EQUIVALENCE

    temp_dep, exist_dep = matrix.get_dependency("A", "C")
    assert temp_dep.type == TemporalType.EVENTUAL
    assert exist_dep.type == ExistentialType.EQUIVALENCE

    temp_dep, exist_dep = matrix.get_dependency("C", "A")
    assert temp_dep == None
    assert exist_dep.type == ExistentialType.EQUIVALENCE

    temp_dep, exist_dep = matrix.get_dependency("B", "A")
    assert temp_dep == None
    assert exist_dep.type == ExistentialType.EQUIVALENCE

def test_variants_to_matrix_XOR():
    variants = [["A", "B"],["A", "C"]]

    matrix = variants_to_matrix(variants)

    assert matrix.activities == ["A", "B", "C"]

    temp_dep, exist_dep = matrix.get_dependency("B", "C")
    assert temp_dep.type == TemporalType.INDEPENDENCE
    assert exist_dep.type == ExistentialType.NEGATED_EQUIVALENCE

    temp_dep, exist_dep = matrix.get_dependency("A", "B")
    assert temp_dep.type == TemporalType.DIRECT
    assert exist_dep.type == ExistentialType.IMPLICATION

    temp_dep, exist_dep = matrix.get_dependency("A", "C")
    assert temp_dep.type == TemporalType.DIRECT
    assert exist_dep.type == ExistentialType.IMPLICATION

def test_empty_variants():
    assert variants_to_matrix([]) == AdjacencyMatrix([])