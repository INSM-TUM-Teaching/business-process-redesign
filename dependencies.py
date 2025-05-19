from enum import Enum, auto
from dataclasses import dataclass

class TemporalType(Enum):
    """
    Defines the type of temporal relationship between two activities.
    """
    DIRECT_PRECEDES = auto()  # A <d B: Termination of A directly enables B.
    EVENTUAL_PRECEDES = auto()  # A <e B: B eventually follows A.
    INDEPENDENCE = auto() # A and B are temporally independent.

@dataclass
class TemporalDependency:
    """
    Represents a temporal dependency between two activities.
    The direction is implicit from the (source, target) key in the main matrix.
    - If (A, B) maps to TemporalDependency(type=TemporalType.DIRECT_PRECEDES), it means A <d B.
    - If (A, B) maps to TemporalDependency(type=TemporalType.EVENTUAL_PRECEDES), it means A <e B.
    """
    type: TemporalType

class ExistentialType(Enum):
    """
    Defines the type of existential dependency between two activities.
    """
    IMPLICATION = auto()  # A => B: If A occurs, B must occur or must have occurred.
    EQUIVALENCE = auto()  # A <=> B: A => B and B => A.
    NEGATED_EQUIVALENCE = auto()  # A <~> B: Either A or B occurs (exclusive OR).
    NAND = auto()  # A | B: If A occurs, B does not, and vice versa; or neither occurs.
    OR = auto()  # A v B: At least one of A or B must occur.
    INDEPENDENCE = auto() # A and B are existentially independent.

@dataclass
class ExistentialDependency:
    """
    Represents an existential dependency between two activities.
    The direction is implicit from the (source, target) key in the main matrix.
    For symmetric relationships (EQUIVALENCE, NEGATED_EQUIVALENCE, NAND, INDEPENDENCE),
    the entry (A,B) would be the same as (B,A).
    For IMPLICATION and OR, the direction matters.
    - If (A, B) maps to ExistentialDependency(type=ExistentialType.IMPLICATION), it means A => B.
    - If (A, B) maps to ExistentialDependency(type=ExistentialType.OR), it means A v B.
    """
    type: ExistentialType
