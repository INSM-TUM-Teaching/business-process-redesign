from typing import List, Set
from adjacency_matrix import AdjacencyMatrix
from dependencies import ExistentialDependency, ExistentialType, TemporalDependency, TemporalType

def get_existential_relation_type(a, b, combinations) -> ExistentialType:
    exists_neither = False
    exists_both = False
    exists_only_a = False
    exists_only_b = False
    for combination in combinations:
        if (a in combination) and (b in combination):
            exists_both = True
        elif (a not in combination) and (b not in combination):
            exists_neither = True
        elif (a in combination) and (b not in combination):
            exists_only_a = True
        elif (a not in combination) and (b in combination):
            exists_only_b = True
    
    if (not exists_only_a) and (not exists_only_b):
        return ExistentialType.EQUIVALENCE
    if not exists_only_a:
        return ExistentialType.IMPLICATION
    if not exists_only_b:
        #change to other dir
        return ExistentialType.IMPLICATION
    if (not exists_neither) and (not exists_both):
        return ExistentialType.NEGATED_EQUIVALENCE
    if not exists_both:
        return ExistentialType.NAND
    if not exists_neither:
        return ExistentialType.OR
    return ExistentialType.INDEPENDENCE

def get_temporal_relation_type(a, b, variants: List[List[str]]) -> TemporalType:
    exists_a_before_b = False
    exists_b_before_a = False
    exists_a_not_direct_before_b = False
    exists_b_not_direct_before_a = False

    for variant in variants:
        if not((a in variant) and (b in variant)):
            continue
        pos_a = variant.index(a)
        pos_b = variant.index(b)
        if pos_a < pos_b:
            exists_a_before_b = True
            if pos_a + 1 != pos_b:
                exists_a_not_direct_before_b = True
        else:
            exists_b_before_a = True
            if pos_a != pos_b + 1:
                exists_b_not_direct_before_a = True

    
    if exists_a_before_b and not exists_b_before_a and not exists_a_not_direct_before_b:
        return TemporalType.DIRECT #a<_d b
    if exists_a_before_b and not exists_b_before_a:
        return TemporalType.EVENTUAL #a< b
    if exists_b_before_a and not exists_a_before_b and not exists_b_not_direct_before_a:
        #add a >_d b
        return None
    if exists_b_before_a and not exists_a_before_b:
        #add a > b
        return None
    return TemporalType.INDEPENDENCE

def variants_to_matrix(variants: List[List[str]]) -> AdjacencyMatrix:
    activities: Set[str] = set()
    for variant in variants:
        activities.update(variant)

    activity_list = list(activities)
    activity_list.sort()
    matrix = AdjacencyMatrix(activity_list)

    combinations = set(frozenset(variant) for variant in variants)

    for activity_a in activities:
        for activity_b in activities:
            if activity_a == activity_b:
                continue
            existential_type = get_existential_relation_type(activity_a, activity_b, combinations)
            temporal_type = get_temporal_relation_type(activity_a, activity_b, variants)


            exist_dep = ExistentialDependency(existential_type)
            temp_dep = ExistentialDependency(temporal_type) if temporal_type is not None else None

            matrix.add_dependency(activity_a, activity_b, temp_dep, exist_dep)
    
    return matrix