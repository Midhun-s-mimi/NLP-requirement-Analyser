from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Path  # <--- ADDED 'Path' HERE
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from app.core.config import settings
from app.db.database import engine, get_db
from app.db import models
from app.schemas.requirement import (
    AnalysisRequest, AnalysisResponse, IssueSchema,
    RefineRequest, RefineResponse, DecisionRequest, DecisionResponse,
    PairTextsRequest, SimilarityResponse, ContradictionResponse,
    RequirementListItem, StatsResponse,
)
from app.services.nlp_service import NLPService
import app.services.nlp_service as nlp_module

# Create database tables on startup if they don't exist
models.Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load AI models once
    nlp_module.nlp_service = NLPService(
        settings.CLASSIFIER_MODEL_PATH,
        similarity_threshold=settings.SIMILARITY_THRESHOLD,
    )
    yield
    # Shutdown
    print("Shutting down...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_service() -> NLPService:
    if nlp_module.nlp_service is None:
        raise HTTPException(status_code=503, detail="AI models are still loading.")
    return nlp_module.nlp_service

@app.get("/health")
def health_check():
    return {"status": "healthy", "models_loaded": nlp_module.nlp_service is not None}

@app.post("/api/v1/analyze", response_model=AnalysisResponse)
def analyze_requirement(request: AnalysisRequest, db: Session = Depends(get_db)):
    service = get_service()
    result = service.analyze_requirement(request.requirement_text)

    # Save Requirement
    db_req = models.Requirement(text=request.requirement_text, project_id=request.project_id)
    db.add(db_req)
    db.commit()
    db.refresh(db_req)

    # Save Analysis
    db_analysis = models.RequirementAnalysis(
        requirement_id=db_req.id,
        clarity_label=result["clarity_label"],
        confidence_score=result["confidence_score"],
        quality_score=result["quality_score"],
        suggested_refinement=result["suggested_refinement"],
        status="pending",
    )
    db.add(db_analysis)
    db.flush()

    # Save Issues
    for issue in result["issues"]:
        db.add(models.DetectedIssue(
            analysis_id=db_analysis.id,
            matched_phrase=issue["matched_phrase"],
            category=issue["category"],
            severity=issue["severity"],
            question=issue["question"],
        ))
    
    db.commit()
    db.refresh(db_analysis)

    return AnalysisResponse(
        requirement_id=db_req.id,
        analysis_id=db_analysis.id,
        original_text=db_req.text,
        clarity_label=result["clarity_label"],
        confidence_score=result["confidence_score"],
        quality_score=result["quality_score"],
        is_ambiguous=result["is_ambiguous"],
        issues=[IssueSchema(**i) for i in result["issues"]],
        suggested_refinement=result["suggested_refinement"],
        status=db_analysis.status,
    )

@app.post("/api/v1/refine", response_model=RefineResponse)
def refine_requirement(request: RefineRequest, db: Session = Depends(get_db)):
    service = get_service()
    db_req = db.get(models.Requirement, request.requirement_id)
    if not db_req:
        raise HTTPException(status_code=404, detail="Requirement not found.")
    
    try:
        result = service.refine_requirement(db_req.text, request.values)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
        
    return RefineResponse(requirement_id=db_req.id, **result)

@app.post("/api/v1/requirements/{requirement_id}/decision", response_model=DecisionResponse)
def record_decision(requirement_id: int, request: DecisionRequest, db: Session = Depends(get_db)):
    db_req = db.get(models.Requirement, requirement_id)
    if not db_req:
        raise HTTPException(status_code=404, detail="Requirement not found.")
    
    analysis = (
        db.query(models.RequirementAnalysis)
        .filter(models.RequirementAnalysis.requirement_id == requirement_id)
        .order_by(models.RequirementAnalysis.id.desc())
        .first()
    )
    if not analysis:
        raise HTTPException(status_code=404, detail="No analysis found for this requirement.")
    
    analysis.status = request.status
    analysis.final_text = request.final_text
    db.commit()
    
    return DecisionResponse(requirement_id=requirement_id, status=request.status, final_text=request.final_text)

@app.get("/api/v1/requirements", response_model=List[RequirementListItem])
def list_requirements(db: Session = Depends(get_db)):
    reqs = db.query(models.Requirement).order_by(models.Requirement.id.desc()).all()
    out = []
    for r in reqs:
        latest = (
            db.query(models.RequirementAnalysis)
            .filter(models.RequirementAnalysis.requirement_id == r.id)
            .order_by(models.RequirementAnalysis.id.desc())
            .first()
        )
        out.append(RequirementListItem(
            requirement_id=r.id,
            text=r.text,
            created_at=r.created_at,
            clarity_label=latest.clarity_label if latest else None,
            quality_score=latest.quality_score if latest else None,
            status=latest.status if latest else None,
        ))
    return out

@app.get("/api/v1/stats", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    analyses = db.query(models.RequirementAnalysis).all()
    total_reqs = db.query(models.Requirement).count()

    def norm(label):
        return (label or "").replace("-", "_").upper()

    labels = [norm(a.clarity_label) for a in analyses]
    scores = [a.quality_score for a in analyses if a.quality_score is not None]
    
    return StatsResponse(
        total_requirements=total_reqs,
        ambiguous_count=labels.count("AMBIGUOUS"),
        incomplete_count=labels.count("INCOMPLETE"),
        non_testable_count=labels.count("NON_TESTABLE"),
        clear_count=labels.count("CLEAR"),
        approved_count=sum(1 for a in analyses if a.status == "approved"),
        rejected_count=sum(1 for a in analyses if a.status == "rejected"),
        average_quality_score=round(sum(scores) / len(scores), 2) if scores else 0.0,
    )

@app.post("/api/v1/similarity", response_model=SimilarityResponse)
def similarity(request: PairTextsRequest):
    service = get_service()
    return SimilarityResponse(**service.compare_similarity(request.text_a, request.text_b))

@app.post("/api/v1/contradiction", response_model=ContradictionResponse)
def contradiction(request: PairTextsRequest):
    service = get_service()
    return ContradictionResponse(**service.check_contradiction(request.text_a, request.text_b))

# --- NEW ENDPOINT FOR DETAILS (Fixed & Cleaned) ---
@app.get("/api/v1/requirements/{requirement_id}", response_model=AnalysisResponse)
def get_requirement_detail(
    requirement_id: int = Path(..., title="Requirement ID"), 
    db: Session = Depends(get_db)
):
    # 1. Get the Requirement
    db_req = db.get(models.Requirement, requirement_id)
    if not db_req:
        raise HTTPException(status_code=404, detail="Requirement not found.")
    
    # 2. Get the Latest Analysis
    latest_analysis = (
        db.query(models.RequirementAnalysis)
        .filter(models.RequirementAnalysis.requirement_id == requirement_id)
        .order_by(models.RequirementAnalysis.id.desc())
        .first()
    )
    
    if not latest_analysis:
        raise HTTPException(status_code=404, detail="No analysis found for this requirement.")
    
    # 3. Get Associated Issues
    issues = (
        db.query(models.DetectedIssue)
        .filter(models.DetectedIssue.analysis_id == latest_analysis.id)
        .all()
    )
    
    # 4. Return Combined Data
    return AnalysisResponse(
        requirement_id=db_req.id,
        analysis_id=latest_analysis.id,
        original_text=db_req.text,
        clarity_label=latest_analysis.clarity_label,
        confidence_score=latest_analysis.confidence_score,
        quality_score=latest_analysis.quality_score,
        is_ambiguous=latest_analysis.clarity_label == "AMBIGUOUS",
        issues=[IssueSchema(
            matched_phrase=i.matched_phrase,
            category=i.category,
            severity=i.severity,
            question=i.question
        ) for i in issues],
        suggested_refinement=latest_analysis.suggested_refinement,
        status=latest_analysis.status,
    )