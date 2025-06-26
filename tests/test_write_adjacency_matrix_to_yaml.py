import pytest
from adjacency_matrix import AdjacencyMatrix, write_adjacency_matrix_to_yaml, parse_yaml_to_adjacency_matrix
from dependencies import TemporalDependency, ExistentialDependency, TemporalType, ExistentialType

def test_write_adjacency_matrix_to_yaml():
    matrix = AdjacencyMatrix(activities=["A", "B", "C", "D"])

    matrix.add_dependency("A", "B",TemporalDependency(TemporalType.INDEPENDENCE), ExistentialDependency(ExistentialType.EQUIVALENCE))
    matrix.add_dependency("A", "C",TemporalDependency(TemporalType.EVENTUAL), ExistentialDependency(ExistentialType.EQUIVALENCE))
    matrix.add_dependency("A", "D",TemporalDependency(TemporalType.EVENTUAL), ExistentialDependency(ExistentialType.EQUIVALENCE))
    matrix.add_dependency("B", "C",TemporalDependency(TemporalType.INDEPENDENCE), ExistentialDependency(ExistentialType.EQUIVALENCE))
    matrix.add_dependency("B", "D",TemporalDependency(TemporalType.EVENTUAL), ExistentialDependency(ExistentialType.EQUIVALENCE))
    matrix.add_dependency("C", "D",TemporalDependency(TemporalType.INDEPENDENCE), ExistentialDependency(ExistentialType.EQUIVALENCE))

    write_adjacency_matrix_to_yaml(matrix, "sample-matrices/non-blockstructured.yaml")
    parsed_matrix = parse_yaml_to_adjacency_matrix("sample-matrices/non-blockstructured.yaml")


    assert parsed_matrix == matrix