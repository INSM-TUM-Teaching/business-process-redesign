from traces_to_matrix import (
    has_implication,
    check_negated_equivalence,
    infer_existential_dependency,
    check_single_trace_temporal_relations,
    infer_temporal_dependency,
    traces_to_adjacency_matrix,
    InferredTemporalPattern,
    InferredDirection,
)
from dependencies import (
    TemporalDependency,
    ExistentialDependency,
    TemporalType,
    ExistentialType,
    Direction,
)


def test_has_implication_logic():
    traces = [
        ["A", "B", "C", "D"],
        ["A", "C", "B", "D"],
        ["A", "E", "D"],
        ["A", "D"],
    ]
    activities = ["A", "B", "C", "D", "E"]

    # Pairs where 'from' implies 'to'
    true_implications = {
        ("A", "D"),
        ("B", "A"),
        ("B", "C"),
        ("B", "D"),
        ("C", "A"),
        ("C", "B"),
        ("C", "D"),
        ("D", "A"),
        ("E", "A"),
        ("E", "D"),
    }

    for from_act in activities:
        for to_act in activities:
            expected = (from_act, to_act) in true_implications or from_act == to_act
            assert (
                has_implication(from_act, to_act, traces, 1.0) == expected
            ), f"{from_act}=>{to_act} failed"


def test_check_negated_equivalence():
    # A <~> B: (A and not B) or (not A and B)
    traces_xor = [["A", "C"], ["B", "D"]]
    assert check_negated_equivalence("A", "B", traces_xor, 1.0) is True

    traces_not_xor = [["A", "B"], ["C"]]
    assert check_negated_equivalence("A", "B", traces_not_xor, 1.0) is False


def test_infer_existential_dependency_same_activity():
    traces = [["A", "B", "C", "C", "A"]]
    assert infer_existential_dependency("A", "A", traces, 1.0) is None


def test_infer_existential_equivalence():
    traces = [["A", "B"], ["C"]]  # A <=> B
    expected = (ExistentialDependency(type=ExistentialType.EQUIVALENCE, direction=Direction.BOTH), "A", "B")
    assert infer_existential_dependency("A", "B", traces, 1.0) == expected


def test_infer_existential_implication():
    traces = [["A", "B"], ["A"], ["B", "C"]]
    assert infer_existential_dependency("A", "B", traces, 1.0) is None

    traces_a_implies_b = [["A", "B"], ["B"], ["C"]]
    expected_ab = (
        ExistentialDependency(
            type=ExistentialType.IMPLICATION, direction=Direction.FORWARD
        ),
        "A",
        "B",
    )
    expected_ba = (
        ExistentialDependency(
            type=ExistentialType.IMPLICATION, direction=Direction.BACKWARD
        ),
        "B",
        "A",
    )
    assert (
        infer_existential_dependency("A", "B", traces_a_implies_b, 1.0) == expected_ab
    )
    assert (
        infer_existential_dependency("B", "A", traces_a_implies_b, 1.0) == expected_ba
    )


def test_check_single_trace_temporal_relations_independence():
    trace = ["A", "B", "C", "C", "A"]
    expected = [
        (InferredTemporalPattern.EVENTUAL, InferredDirection.FORWARD),
        (InferredTemporalPattern.DIRECT, InferredDirection.BACKWARD),
    ]
    assert check_single_trace_temporal_relations("A", "C", trace) == expected


def test_infer_temporal_dependency_independence():
    traces = [["A", "B", "C", "C", "A"]]
    assert infer_temporal_dependency("A", "C", traces, 1.0) is None

def test_traces_to_adj_matrix_simple_variant():
    traces = [["A", "B", "C"]]
    adj_matrix = traces_to_adjacency_matrix(
        traces, temporal_threshold=1.0, existential_threshold=1.0
    )
    assert sorted(adj_matrix.activities) == ["A", "B", "C"]

    # A->B
    dep_ab_temp, dep_ab_exist = adj_matrix.get_dependency("A", "B")
    assert dep_ab_temp == TemporalDependency(TemporalType.DIRECT, Direction.FORWARD)
    assert dep_ab_exist == ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)

    # B->C
    dep_bc_temp, dep_bc_exist = adj_matrix.get_dependency("B", "C")
    assert dep_bc_temp == TemporalDependency(TemporalType.DIRECT, Direction.FORWARD)
    assert dep_bc_exist == ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)

    # A->C
    dep_ac_temp, dep_ac_exist = adj_matrix.get_dependency("A", "C")
    assert dep_ac_temp == TemporalDependency(TemporalType.EVENTUAL, Direction.FORWARD)
    assert dep_ac_exist == ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)

    # B->A (should be symmetric existential, no specific A->B temporal means no B->A temporal)
    dep_ba_temp, dep_ba_exist = adj_matrix.get_dependency("B", "A")
    assert dep_ba_temp == TemporalDependency(TemporalType.DIRECT, Direction.BACKWARD)
    assert dep_ba_exist == ExistentialDependency(ExistentialType.EQUIVALENCE, Direction.BOTH)


def test_traces_to_adj_matrix_choice():
    traces = [["A", "B"], ["A", "C"]]

    adj_matrix = traces_to_adjacency_matrix(
        traces, temporal_threshold=1.0, existential_threshold=1.0
    )

    assert sorted(adj_matrix.activities) == ["A", "B", "C"]

    dep_ab_t, dep_ab_e = adj_matrix.get_dependency("A", "B")
    assert dep_ab_t == TemporalDependency(TemporalType.DIRECT, Direction.FORWARD)
    assert dep_ab_e == ExistentialDependency(
        ExistentialType.IMPLICATION, Direction.BACKWARD
    )

    dep_ac_t, dep_ac_e = adj_matrix.get_dependency("A", "C")
    assert dep_ac_t == TemporalDependency(TemporalType.DIRECT, Direction.FORWARD)
    assert dep_ac_e == ExistentialDependency(
        ExistentialType.IMPLICATION, Direction.BACKWARD
    )

    dep_bc_t, dep_bc_e = adj_matrix.get_dependency("B", "C")
    assert dep_bc_t is None
    assert dep_bc_e == ExistentialDependency(
        ExistentialType.NEGATED_EQUIVALENCE, Direction.BOTH
    )


def test_traces_to_adj_matrix_independence():
    traces = [["A", "B", "C", "C", "A"]]
    adj_matrix = traces_to_adjacency_matrix(
        traces, temporal_threshold=1.0, existential_threshold=1.0
    )
    assert sorted(adj_matrix.activities) == ["A", "B", "C"]

    dep_ab_t, dep_ab_e = adj_matrix.get_dependency("A", "B")
    assert dep_ab_t == TemporalDependency(TemporalType.DIRECT, Direction.FORWARD)
    assert dep_ab_e == ExistentialDependency(
        ExistentialType.EQUIVALENCE, Direction.BOTH
    )

    dep_ac_t, dep_ac_e = adj_matrix.get_dependency("A", "C")
    assert dep_ac_t is None
    assert dep_ac_e == ExistentialDependency(
        ExistentialType.EQUIVALENCE, Direction.BOTH
    )

    dep_ba_t, dep_ba_e = adj_matrix.get_dependency("B", "A")
    assert dep_ba_t is None
    assert dep_ba_e == ExistentialDependency(
        ExistentialType.EQUIVALENCE, Direction.BOTH
    )

    dep_ca_t, dep_ca_e = adj_matrix.get_dependency("C", "A")
    assert dep_ca_t is None
    assert dep_ca_e == ExistentialDependency(
        ExistentialType.EQUIVALENCE, Direction.BOTH
    )