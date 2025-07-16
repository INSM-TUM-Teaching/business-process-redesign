from variants_to_matrix import get_existential_relation, get_temporal_relation, variants_to_matrix
from dependencies import ExistentialType, TemporalType, Direction
from adjacency_matrix import AdjacencyMatrix

def test_get_existential():
    variants = [["A", "B"], []]

    combinations = set(frozenset(variant) for variant in variants)

    assert get_existential_relation("A","B", combinations) == (ExistentialType.EQUIVALENCE, Direction.BOTH)

    variants = [["A", "B"], ["B"]]

    combinations = set(frozenset(variant) for variant in variants)

    assert get_existential_relation("A","B", combinations) == (ExistentialType.IMPLICATION, Direction.FORWARD)

    variants = [["A", "B"], ["B"], ["A"]]

    combinations = set(frozenset(variant) for variant in variants)

    assert get_existential_relation("A","B", combinations) == (ExistentialType.OR, Direction.BOTH)

    variants = [[], ["B"], ["A"]]

    combinations = set(frozenset(variant) for variant in variants)

    assert get_existential_relation("A","B", combinations) == (ExistentialType.NAND, Direction.BOTH)

    variants = [["B"], ["A"]]

    combinations = set(frozenset(variant) for variant in variants)

    assert get_existential_relation("A","B", combinations) == (ExistentialType.NEGATED_EQUIVALENCE, Direction.BOTH)

    variants = [["B"], ["A"], [], ["A", "B"]]

    combinations = set(frozenset(variant) for variant in variants)

    assert get_existential_relation("A","B", combinations) == (ExistentialType.INDEPENDENCE, Direction.BOTH)

def test_get_temporal_relation():
    variants = [["A", "B", "C", "D", "E"],["B", "A", "C", "D", "F"]]

    assert get_temporal_relation("A", "B", variants) == (TemporalType.INDEPENDENCE, Direction.BOTH)

    assert get_temporal_relation("C", "D", variants) == (TemporalType.DIRECT, Direction.FORWARD)

    assert get_temporal_relation("A", "C", variants) == (TemporalType.EVENTUAL, Direction.FORWARD)

    assert get_temporal_relation("E", "F", variants) == (None, None)

def test_variants_to_matrix():
    variants = [["A", "B", "C"],["A", "C", "B"]]

    matrix = variants_to_matrix(variants)

    assert matrix.activities == ["A", "B", "C"]

    temp_dep, exist_dep = matrix.get_dependency("B", "C")
    assert temp_dep.type == TemporalType.INDEPENDENCE
    assert temp_dep.direction == Direction.BOTH
    assert exist_dep.type == ExistentialType.EQUIVALENCE
    assert exist_dep.direction == Direction.BOTH

    temp_dep, exist_dep = matrix.get_dependency("A", "B")
    assert temp_dep.type == TemporalType.EVENTUAL
    assert temp_dep.direction == Direction.FORWARD
    assert exist_dep.type == ExistentialType.EQUIVALENCE
    assert exist_dep.direction == Direction.BOTH

    temp_dep, exist_dep = matrix.get_dependency("A", "C")
    assert temp_dep.type == TemporalType.EVENTUAL
    assert temp_dep.direction == Direction.FORWARD
    assert exist_dep.type == ExistentialType.EQUIVALENCE
    assert exist_dep.direction == Direction.BOTH

    temp_dep, exist_dep = matrix.get_dependency("C", "A")
    assert temp_dep.type == TemporalType.EVENTUAL
    assert temp_dep.direction == Direction.BACKWARD
    assert exist_dep.type == ExistentialType.EQUIVALENCE
    assert exist_dep.direction == Direction.BOTH

    temp_dep, exist_dep = matrix.get_dependency("B", "A")
    assert temp_dep.type == TemporalType.EVENTUAL
    assert temp_dep.direction == Direction.BACKWARD
    assert exist_dep.type == ExistentialType.EQUIVALENCE
    assert exist_dep.direction == Direction.BOTH

def test_variants_to_matrix_XOR():
    variants = [["A", "B"],["A", "C"]]

    matrix = variants_to_matrix(variants)

    assert matrix.activities == ["A", "B", "C"]

    temp_dep, exist_dep = matrix.get_dependency("B", "C")
    assert temp_dep is None
    assert exist_dep.type == ExistentialType.NEGATED_EQUIVALENCE
    assert exist_dep.direction == Direction.BOTH