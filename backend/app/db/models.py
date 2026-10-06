from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class Requirement(Base):
    __tablename__ = "requirements"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    project_id = Column(Integer, nullable=True) # Optional grouping
    created_at = Column(DateTime, default=datetime.utcnow)
    
    analyses = relationship("RequirementAnalysis", back_populates="requirement")

class RequirementAnalysis(Base):
    __tablename__ = "analyses"
    id = Column(Integer, primary_key=True, index=True)
    requirement_id = Column(Integer, ForeignKey("requirements.id"))
    clarity_label = Column(String, nullable=True)
    confidence_score = Column(Float, nullable=True)
    quality_score = Column(Float, nullable=True) # 0-100
    suggested_refinement = Column(Text, nullable=True)
    status = Column(String, default="pending") # pending, approved, rejected
    created_at = Column(DateTime, default=datetime.utcnow)
    
    requirement = relationship("Requirement", back_populates="analyses")
    issues = relationship("DetectedIssue", back_populates="analysis")

class DetectedIssue(Base):
    __tablename__ = "detected_issues"
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"))
    matched_phrase = Column(String, nullable=False)
    category = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    question = Column(Text, nullable=True)
    
    analysis = relationship("RequirementAnalysis", back_populates="issues")