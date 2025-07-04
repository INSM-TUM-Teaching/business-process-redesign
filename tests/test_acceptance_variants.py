import pytest
from adjacency_matrix import AdjacencyMatrix, parse_yaml_to_adjacency_matrix
from dependencies import TemporalType, ExistentialType, TemporalDependency, ExistentialDependency, Direction
from acceptance_variants import (
    satisfies_existential_constraints,
    build_permutations,
    satisfies_temporal_constraints,
    generate_acceptance_variants
)

@pytest.fixture
def sample_activities():
    return ["A", "B", "C"]

@pytest.fixture
def sample_adj_matrix(sample_activities):
    matrix = AdjacencyMatrix(activities=sample_activities)
    matrix.add_dependency("A", "B", TemporalDependency(TemporalType.DIRECT, Direction.FORWARD), ExistentialDependency(ExistentialType.IMPLICATION, Direction.FORWARD))
    matrix.add_dependency("B", "C", TemporalDependency(TemporalType.EVENTUAL, Direction.FORWARD), ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH))
    matrix.add_dependency("A", "C", TemporalDependency(TemporalType.INDEPENDENCE, Direction.BOTH), ExistentialDependency(ExistentialType.OR, Direction.BOTH))
    return matrix


def test_satisfies_existential_implication_ok(sample_activities):
    deps = {("A", "B"): ExistentialDependency(ExistentialType.IMPLICATION, Direction.FORWARD)}
    assert satisfies_existential_constraints({"A", "B"}, sample_activities, deps) == True
    assert satisfies_existential_constraints({"B"}, sample_activities, deps) == True
    assert satisfies_existential_constraints(set(), sample_activities, deps) == True
    assert satisfies_existential_constraints({"A", "C"}, sample_activities, deps) == False

def test_satisfies_existential_implication_fail(sample_activities):
    deps = {("A", "B"): ExistentialDependency(ExistentialType.IMPLICATION, Direction.FORWARD)}
    assert satisfies_existential_constraints({"A"}, sample_activities, deps) == False

def test_satisfies_existential_equivalence_ok(sample_activities):
    deps = {("A", "B"): ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)}
    assert satisfies_existential_constraints({"A", "B"}, sample_activities, deps) == True
    assert satisfies_existential_constraints(set(), sample_activities, deps) == True

def test_satisfies_existential_equivalence_fail(sample_activities):
    deps = {("A", "B"): ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)}
    assert satisfies_existential_constraints({"A"}, sample_activities, deps) == False
    assert satisfies_existential_constraints({"B"}, sample_activities, deps) == False

def test_satisfies_existential_or_ok(sample_activities):
    deps = {("A", "B"): ExistentialDependency(ExistentialType.OR, Direction.BOTH)}
    assert satisfies_existential_constraints({"A"}, sample_activities, deps) == True
    assert satisfies_existential_constraints({"B"}, sample_activities, deps) == True
    assert satisfies_existential_constraints({"A", "B"}, sample_activities, deps) == True

def test_satisfies_existential_or_fail(sample_activities):
    deps = {("A", "B"): ExistentialDependency(ExistentialType.OR, Direction.BOTH)}
    assert satisfies_existential_constraints(set(), sample_activities, deps) == False
    assert satisfies_existential_constraints({"C"}, sample_activities, deps) == False # A and B not in subset

def test_satisfies_existential_nand_ok(sample_activities):
    deps = {("A", "B"): ExistentialDependency(ExistentialType.NAND, Direction.BOTH)}
    assert satisfies_existential_constraints({"A"}, sample_activities, deps) == True
    assert satisfies_existential_constraints({"B"}, sample_activities, deps) == True
    assert satisfies_existential_constraints(set(), sample_activities, deps) == True

def test_satisfies_existential_nand_fail(sample_activities):
    deps = {("A", "B"): ExistentialDependency(ExistentialType.NAND, Direction.BOTH)}
    assert satisfies_existential_constraints({"A", "B"}, sample_activities, deps) == False

def test_satisfies_existential_negated_equivalence_ok(sample_activities):
    deps = {("A", "B"): ExistentialDependency(ExistentialType.NEGATED_EQUIVALENCE, Direction.BOTH)}
    assert satisfies_existential_constraints({"A"}, sample_activities, deps) == True
    assert satisfies_existential_constraints({"B"}, sample_activities, deps) == True

def test_satisfies_existential_negated_equivalence_fail(sample_activities):
    deps = {("A", "B"): ExistentialDependency(ExistentialType.NEGATED_EQUIVALENCE, Direction.BOTH)}
    assert satisfies_existential_constraints({"A", "B"}, sample_activities, deps) == False
    assert satisfies_existential_constraints(set(), sample_activities, deps) == False

def test_satisfies_existential_independence(sample_activities):
    deps = {("A", "B"): ExistentialDependency(ExistentialType.INDEPENDENCE, Direction.BOTH)}
    assert satisfies_existential_constraints({"A", "B"}, sample_activities, deps) == True
    assert satisfies_existential_constraints({"A"}, sample_activities, deps) == True
    assert satisfies_existential_constraints(set(), sample_activities, deps) == True

def test_build_permutations_empty():
    assert build_permutations(set()) == [[]]

def test_build_permutations_single():
    perms = build_permutations({"A"})
    assert len(perms) == 1
    assert sorted(perms[0]) == sorted(["A"])

def test_build_permutations_multiple():
    perms = build_permutations({"A", "B"})
    assert len(perms) == 2
    assert sorted([tuple(sorted(p)) for p in perms]) == sorted([("A", "B"), ("A", "B")])
    assert ['A', 'B'] in perms or ['B', 'A'] in perms
    assert ['B', 'A'] in perms or ['A', 'B'] in perms

def test_satisfies_temporal_direct_ok():
    deps = {("A", "B"): TemporalDependency(TemporalType.DIRECT, Direction.FORWARD)}
    assert satisfies_temporal_constraints(["A", "B"], deps) == True
    assert satisfies_temporal_constraints(["X", "A", "B", "Y"], deps) == True

def test_satisfies_temporal_direct_fail():
    deps = {("A", "B"): TemporalDependency(TemporalType.DIRECT, Direction.FORWARD)}
    assert satisfies_temporal_constraints(["B", "A"], deps) == False
    assert satisfies_temporal_constraints(["A", "X", "B"], deps) == False
    assert satisfies_temporal_constraints(["A"], deps) == True
    assert satisfies_temporal_constraints(["B"], deps) == True

def test_satisfies_temporal_eventual_ok():
    deps = {("A", "B"): TemporalDependency(TemporalType.EVENTUAL, Direction.FORWARD)}
    assert satisfies_temporal_constraints(["A", "B"], deps) == True
    assert satisfies_temporal_constraints(["A", "X", "B"], deps) == True

def test_satisfies_temporal_eventual_fail():
    deps = {("A", "B"): TemporalDependency(TemporalType.EVENTUAL, Direction.FORWARD)}
    assert satisfies_temporal_constraints(["B", "A"], deps) == False
    assert satisfies_temporal_constraints(["B", "X", "A"], deps) == False

def test_satisfies_temporal_independence():
    deps = {("A", "B"): TemporalDependency(TemporalType.INDEPENDENCE, Direction.BOTH)}
    assert satisfies_temporal_constraints(["A", "B"], deps) == True
    assert satisfies_temporal_constraints(["B", "A"], deps) == True
    assert satisfies_temporal_constraints(["A", "X", "B"], deps) == True

def test_satisfies_temporal_empty_sequence():
    assert satisfies_temporal_constraints([], {}) == True

def test_generate_acceptance_variants_simple_direct_implication():
    adj = AdjacencyMatrix(activities=["A", "B"])
    adj.add_dependency("A", "B", TemporalDependency(TemporalType.DIRECT, Direction.FORWARD), ExistentialDependency(ExistentialType.IMPLICATION, Direction.FORWARD))
    variants = generate_acceptance_variants(adj)
    
    expected_variants = sorted([[], ["B"], ["A", "B"]])
    assert len(variants) == len(expected_variants)
    assert sorted(variants) == expected_variants

def test_generate_acceptance_variants_simple_eventual_equivalence():
    adj = AdjacencyMatrix(activities=["A", "B"])
    adj.add_dependency("A", "B", TemporalDependency(TemporalType.EVENTUAL, Direction.FORWARD), ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH))
    variants = generate_acceptance_variants(adj)
    assert sorted(variants) == sorted([[], ["A", "B"]])

def test_generate_acceptance_variants_choice_or():
    adj = AdjacencyMatrix(activities=["A", "B"])
    adj.add_dependency("A", "B", None, ExistentialDependency(ExistentialType.OR, Direction.BOTH))
    adj.add_dependency("B", "A", None, ExistentialDependency(ExistentialType.OR, Direction.BOTH))

    variants = generate_acceptance_variants(adj)
    expected = sorted([["A"], ["B"], ["A", "B"], ["B", "A"]])
    assert sorted([sorted(s) for s in variants]) == sorted([sorted(s) for s in expected])

def test_generate_acceptance_variants_from_yaml_first_prototype():
    yaml_file_path = "sample-matrices/first_prototype.yaml"
    adj_matrix = parse_yaml_to_adjacency_matrix(yaml_file_path)
    variants = generate_acceptance_variants(adj_matrix)

    found_ABCE = False
    for variant in variants:
        if variant == ['A', 'B', 'C', 'E']:
            found_ABCE = True
        if 'C' in variant and 'D' in variant:
            pytest.fail(f"Variant {variant} contains both C and D, which violates C|D NAND constraint.")

    assert found_ABCE, "Expected variant [A,B,C,E] not found."

    adj_indep = AdjacencyMatrix(activities=["X", "Y"])
    adj_indep.add_dependency("X", "Y", TemporalDependency(TemporalType.INDEPENDENCE, Direction.BOTH), ExistentialDependency(ExistentialType.INDEPENDENCE, Direction.BOTH))
    adj_indep.add_dependency("Y", "X", TemporalDependency(TemporalType.INDEPENDENCE, Direction.BOTH), ExistentialDependency(ExistentialType.INDEPENDENCE, Direction.BOTH))
    adj_indep.add_dependency("X", "X", TemporalDependency(TemporalType.INDEPENDENCE, Direction.BOTH), ExistentialDependency(ExistentialType.INDEPENDENCE, Direction.BOTH))
    adj_indep.add_dependency("Y", "Y", TemporalDependency(TemporalType.INDEPENDENCE, Direction.BOTH), ExistentialDependency(ExistentialType.INDEPENDENCE, Direction.BOTH))
    
    variants_indep = generate_acceptance_variants(adj_indep)
    expected_indep = sorted([[], ["X"], ["Y"], ["X","Y"], ["Y","X"]])
    actual_indep = sorted([list(s) for s in variants_indep])
    assert actual_indep == expected_indep, f"Expected {expected_indep}, got {actual_indep}"