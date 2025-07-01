from typing import List, Set, Optional, Tuple
from enum import Enum

from adjacency_matrix import AdjacencyMatrix
from dependencies import (
    TemporalDependency,
    ExistentialDependency,
    TemporalType,
    ExistentialType,
)
from constraint_logic import (
    evaluate_implication,
    evaluate_negated_equivalence,
    is_directly_follows,
    is_eventually_follows,
)


class InferredDirection(Enum):
    FORWARD = "FORWARD"
    BACKWARD = "BACKWARD"


class InferredTemporalPattern(Enum):
    DIRECT = "DIRECT"
    EVENTUAL = "EVENTUAL"


# --- Temporal Dependency Check ---


def get_activity_positions(trace: List[str], activity: str) -> List[int]:
    return [i for i, act in enumerate(trace) if act == activity]


def check_single_trace_temporal_relations(
    from_activity: str,
    to_activity: str,
    trace: List[str],
) -> List[Tuple[InferredTemporalPattern, InferredDirection]]:
    """
    Identifies temporal patterns (Direct/Eventual) and directions (Forward/Backward)
    between from_activity and to_activity instances within a single trace.
    """
    relations: List[Tuple[InferredTemporalPattern, InferredDirection]] = []
    from_positions = get_activity_positions(trace, from_activity)
    to_positions = get_activity_positions(trace, to_activity)

    if not from_positions or not to_positions:
        return []

    # Edge case where `from` and `to` are the same
    if from_activity == to_activity:
        for i in range(len(from_positions)):
            for j in range(i + 1, len(from_positions)):
                pos1, pos2 = from_positions[i], from_positions[j]
                pattern = (
                    InferredTemporalPattern.DIRECT
                    if is_directly_follows(pos1, pos2)
                    else InferredTemporalPattern.EVENTUAL
                )
                relations.append((pattern, InferredDirection.FORWARD))
        return relations

    from_idx, to_idx = 0, 0
    while from_idx < len(from_positions) and to_idx < len(to_positions):
        pos_f = from_positions[from_idx]
        pos_t = to_positions[to_idx]

        if is_eventually_follows(
            pos_f, pos_t
        ):  # from_activity instance before to_activity instance
            pattern = (
                InferredTemporalPattern.DIRECT
                if is_directly_follows(pos_f, pos_t)
                else InferredTemporalPattern.EVENTUAL
            )
            relations.append((pattern, InferredDirection.FORWARD))
            from_idx += 1
            to_idx += 1  # Both pointers advance
        elif is_eventually_follows(
            pos_t, pos_f
        ):  # to_activity instance before from_activity instance
            pattern = (
                InferredTemporalPattern.DIRECT
                if is_directly_follows(pos_t, pos_f)
                else InferredTemporalPattern.EVENTUAL
            )
            relations.append((pattern, InferredDirection.BACKWARD))
            to_idx += 1  # Only to_pointer advances, current from_instance might relate to later to_instance
        else:  # pos_f == pos_t. Should not happen if from_activity != to_activity.
            to_idx += 1  # Advance one pointer to avoid infinite loop
    return relations


def classify_aggregate_temporal_relations(
    all_relations: List[Tuple[InferredTemporalPattern, InferredDirection]],
    threshold: float,
) -> Optional[Tuple[TemporalType, InferredDirection]]:
    """
    Aggregates all found temporal relations from traces to determine a single dominant
    TemporalDependency type and direction.
    """
    if not all_relations:
        return None

    total_relations_count = len(all_relations)

    forward_relations = [
        rel for rel in all_relations if rel[1] == InferredDirection.FORWARD
    ]
    backward_relations = [
        rel for rel in all_relations if rel[1] == InferredDirection.BACKWARD
    ]

    forward_count = len(forward_relations)
    backward_count = len(backward_relations)

    forward_ratio = (
        forward_count / total_relations_count if total_relations_count > 0 else 0
    )
    backward_ratio = (
        backward_count / total_relations_count if total_relations_count > 0 else 0
    )

    final_direction: Optional[InferredDirection] = None
    relations_for_type_decision: List[
        Tuple[InferredTemporalPattern, InferredDirection]
    ] = []

    # Determine dominant direction (first if both meet threshold and forward_ratio is higher)
    if forward_ratio >= threshold and forward_ratio >= backward_ratio:
        final_direction = InferredDirection.FORWARD
        relations_for_type_decision = forward_relations
    elif backward_ratio >= threshold:  # check backward only if forward condition failed
        final_direction = InferredDirection.BACKWARD
        relations_for_type_decision = backward_relations
    else:
        return None  # No dominant direction meets threshold criteria

    if not relations_for_type_decision:  # Should not happen if final_direction is set
        return None

    # if any relation (in the set supporting the chosen direction) is Eventual, then Eventual.
    has_eventual = any(
        pat == InferredTemporalPattern.EVENTUAL
        for pat, _ in relations_for_type_decision
    )

    final_temporal_type = TemporalType.EVENTUAL if has_eventual else TemporalType.DIRECT

    return final_temporal_type, final_direction


def infer_temporal_dependency(
    from_activity: str,
    to_activity: str,
    traces: List[List[str]],
    threshold: float,
) -> Optional[Tuple[TemporalDependency, str, str]]:
    """
    Infers the dominant temporal dependency between from_activity and to_activity.
    Returns (TemporalDependency, source_activity, target_activity) or None.
    """
    if not traces:
        return None

    all_discovered_relations: List[
        Tuple[InferredTemporalPattern, InferredDirection]
    ] = []
    for trace in traces:
        trace_relations = check_single_trace_temporal_relations(
            from_activity, to_activity, trace
        )
        all_discovered_relations.extend(trace_relations)

    if not all_discovered_relations:
        return None

    classified_result = classify_aggregate_temporal_relations(
        all_discovered_relations, threshold
    )

    if classified_result:
        dep_type, direction = classified_result
        if direction == InferredDirection.FORWARD:
            return TemporalDependency(type=dep_type), from_activity, to_activity
        else:  # InferredDirection.BACKWARD
            return (
                TemporalDependency(type=dep_type),
                to_activity,
                from_activity,
            )  # Reversed source/target

    return None


# --- Existential Dependency Check ---


def has_implication(
    from_activity: str,
    to_activity: str,
    traces: List[List[str]],
    threshold: float,
) -> bool:
    """
    Checks if `from_activity` implies `to_activity` in the traces.
    (from => to is true if all traces containing 'from' also contain 'to')
    """
    total_traces = len(traces)
    if total_traces == 0:
        return threshold == 0.0

    traces_where_antecedent_present = 0
    valid_implications = 0

    for trace in traces:
        from_present = from_activity in trace
        to_present = to_activity in trace

        if from_present:
            traces_where_antecedent_present += 1
            if evaluate_implication(from_present, to_present):
                valid_implications += 1

    if traces_where_antecedent_present == 0:
        return True

    calculated_ratio = valid_implications / traces_where_antecedent_present
    return calculated_ratio >= threshold


def check_negated_equivalence(
    activity1: str,
    activity2: str,
    traces: List[List[str]],
    threshold: float,
) -> bool:
    """
    Checks for negated equivalence (XOR) between activity1 and activity2.
    (act1 <~> act2 is true if traces with (act1 or act2) have exactly one of them)
    """

    relevant_traces = [
        trace for trace in traces if activity1 in trace or activity2 in trace
    ]  # traces containing at least one of the activities

    if not relevant_traces:
        return threshold == 0.0

    valid_for_neg_equiv_count = 0
    for trace in relevant_traces:
        act1_present = activity1 in trace
        act2_present = activity2 in trace
        if evaluate_negated_equivalence(act1_present, act2_present):
            valid_for_neg_equiv_count += 1

    calculated_ratio = valid_for_neg_equiv_count / len(relevant_traces)
    return calculated_ratio >= threshold


def infer_existential_dependency(
    activity_a: str,
    activity_b: str,
    traces: List[List[str]],
    threshold: float,
) -> Optional[Tuple[ExistentialDependency, str, str]]:
    """
    Infers existential dependency between activity_a and activity_b.
    Returns (ExistentialDependency, source_activity, target_activity) or None.
    """
    if activity_a == activity_b:
        return None

    a_implies_b = has_implication(activity_a, activity_b, traces, threshold)
    b_implies_a = has_implication(activity_b, activity_a, traces, threshold)

    if a_implies_b and b_implies_a:
        return (
            ExistentialDependency(type=ExistentialType.EQUIVALENCE),
            activity_a,
            activity_b,
        )
    if a_implies_b:
        return (
            ExistentialDependency(type=ExistentialType.IMPLICATION),
            activity_a,
            activity_b,
        )
    if b_implies_a:
        return (
            ExistentialDependency(type=ExistentialType.IMPLICATION),
            activity_b,
            activity_a,
        )

    if check_negated_equivalence(activity_a, activity_b, traces, threshold):
        return (
            ExistentialDependency(type=ExistentialType.NEGATED_EQUIVALENCE),
            activity_a,
            activity_b,
        )

    return None


def traces_to_adjacency_matrix(
    traces: List[List[str]],
    temporal_threshold: float = 1.0,  # Default threshold for temporal relations
    existential_threshold: float = 1.0,  # Default threshold for existential relations
) -> AdjacencyMatrix:
    """
    Converts a list of traces into an AdjacencyMatrix by inferring dependencies.
    """
    if not traces:
        return AdjacencyMatrix(activities=[])

    activities_set: Set[str] = set()
    # Filter out empty traces
    valid_traces = [trace for trace in traces if trace]
    if not valid_traces:
        return AdjacencyMatrix(activities=[])

    for trace in valid_traces:
        activities_set.update(trace)

    sorted_activities = sorted(list(activities_set))
    adj_matrix = AdjacencyMatrix(activities=sorted_activities)

    for act1 in sorted_activities:
        for act2 in sorted_activities:
            # For the matrix cell (act1, act2), we infer dependencies FROM act1 TO act2.

            # infer_temporal_dependency considers (act1, act2) pair and might return a dep for (act1,act2) or (act2,act1)
            temp_dep_info = infer_temporal_dependency(
                act1, act2, valid_traces, temporal_threshold
            )

            final_temporal_dep: Optional[TemporalDependency] = None
            if temp_dep_info:
                td, td_src, td_tgt = temp_dep_info
                if td_src == act1 and td_tgt == act2:
                    final_temporal_dep = td

            # Infer Existential Dependency
            final_existential_dep: Optional[ExistentialDependency] = None
            if act1 == act2:
                pass
            else:
                exist_dep_info = infer_existential_dependency(
                    act1, act2, valid_traces, existential_threshold
                )
                if exist_dep_info:
                    ed, ed_src, ed_tgt = exist_dep_info
                    if ed.type in [
                        ExistentialType.EQUIVALENCE,
                        ExistentialType.NEGATED_EQUIVALENCE,
                    ]:
                        # Symmetric dependencies apply to (act1, act2) if act1, act2 is the pair inferred upon.
                        # The inference for (act1, act2) will be the same as for (act2, act1) for these types.
                        final_existential_dep = ed
                    elif ed.type == ExistentialType.IMPLICATION:
                        if ed_src == act1 and ed_tgt == act2:
                            final_existential_dep = ed

            if final_temporal_dep is not None or final_existential_dep is not None:
                adj_matrix.add_dependency(
                    act1, act2, final_temporal_dep, final_existential_dep
                )

    return adj_matrix
