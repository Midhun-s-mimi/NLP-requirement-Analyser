from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class IssueSchema(BaseModel):
    matched_phrase: str
    category: str
    severity: str
    question: str
    unit: str = ""
    template: str = ""

class AnalysisRequest(BaseModel):
    requirement_text: str = Field(..., min_length=3, max_length=2000)
    project_id: Optional[int] = None

class AnalysisResponse(BaseModel):
    requirement_id: int
    analysis_id: int
    original_text: str
    clarity_label: Optional[str]
    confidence_score: Optional[float] = None
    quality_score: float
    is_ambiguous: bool
    issues: List[IssueSchema]
    suggested_refinement: str
    status: str

class RefineRequest(BaseModel):
    requirement_id: int
    values: List[str] = Field(..., description="One value per detected issue, in order.")

class RefineResponse(BaseModel):
    requirement_id: int
    refined_text: str
    filled_templates: List[str]

class DecisionRequest(BaseModel):
    status: str = Field(..., pattern="^(approved|rejected)$")
    final_text: str

class DecisionResponse(BaseModel):
    requirement_id: int
    status: str
    final_text: str

class PairTextsRequest(BaseModel):
    text_a: str = Field(..., min_length=3, max_length=2000)
    text_b: str = Field(..., min_length=3, max_length=2000)

class SimilarityResponse(BaseModel):
    similarity_score: float
    classification: str
    threshold_used: float

class ContradictionResponse(BaseModel):
    label: str
    confidence: float

class RequirementListItem(BaseModel):
    requirement_id: int
    text: str
    created_at: datetime
    clarity_label: Optional[str] = None
    quality_score: Optional[float] = None
    status: Optional[str] = None

class StatsResponse(BaseModel):
    total_requirements: int
    ambiguous_count: int
    incomplete_count: int
    non_testable_count: int
    clear_count: int
    approved_count: int
    rejected_count: int
    average_quality_score: float