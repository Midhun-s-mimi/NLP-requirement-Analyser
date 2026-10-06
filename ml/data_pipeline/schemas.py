from pydantic import BaseModel, Field
from typing import List
from enum import Enum
import uuid

class ClarityLabel(str, Enum):
    CLEAR = "Clear"
    AMBIGUOUS = "Ambiguous"
    INCOMPLETE = "Incomplete"
    NON_TESTABLE = "Non-testable"

class AmbiguityType(str, Enum):
    PERFORMANCE = "Performance"
    QUANTITY = "Quantity"
    SIZE = "Size"
    TEMPORAL = "Temporal"
    SUBJECTIVE = "Subjective"
    SECURITY = "Security"
    MISSING_CONDITION = "Missing Condition"
    MISSING_CONSTRAINT = "Missing Constraint"
    VAGUE_TERMINOLOGY = "Vague Terminology"

class RequirementRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    requirement_text: str
    domain: str
    clarity_label: ClarityLabel
    ambiguity_types: List[AmbiguityType] = []
    completeness_label: str = "Complete"
    testability_label: str = "Testable"
    source: str = "synthetic"
    annotation_confidence: float = 1.0