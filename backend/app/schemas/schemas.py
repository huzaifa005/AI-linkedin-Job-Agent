"""
Pydantic schemas for API request/response validation.
Separated from SQLModel DB models for clean API boundaries.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# ─── Health ─────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str = "ok"
    version: str
    app_name: str


# ─── CV Schemas ─────────────────────────────────────────────────────────────

class CVUploadResponse(BaseModel):
    cv_id: str
    filename: str
    text_preview: str = Field(description="First 500 characters of extracted text")
    char_count: int
    created_at: datetime


class CVDetailResponse(BaseModel):
    cv_id: str
    filename: str
    raw_text: str
    char_count: int
    created_at: datetime


# ─── Job Schemas ────────────────────────────────────────────────────────────

class JobInput(BaseModel):
    """Schema for a single job listing input."""
    title: str = Field(min_length=1, max_length=500)
    company: str = Field(min_length=1, max_length=255)
    location: str = Field(default="", max_length=500)
    link: str = Field(default="", max_length=2000)


class JobsUploadRequest(BaseModel):
    """Schema for bulk job upload (JSON array)."""
    jobs: List[JobInput] = Field(min_length=1)


# ─── Evaluation Schemas ────────────────────────────────────────────────────

class EvaluateSingleRequest(BaseModel):
    """Evaluate a single job against a CV."""
    cv_id: str
    job: JobInput


class EvaluateBatchRequest(BaseModel):
    """Evaluate multiple jobs against a CV."""
    cv_id: str
    jobs: List[JobInput] = Field(min_length=1)


class EvaluationResult(BaseModel):
    """Result of a single job evaluation."""
    evaluation_id: str
    job_title: str
    company: str
    location: str
    link: str
    score: int
    max_score: int = 18
    reason: str
    is_match: bool
    documents_available: bool = False
    doc_id: Optional[str] = None


class EvaluateSingleResponse(BaseModel):
    """Response for a single job evaluation."""
    result: EvaluationResult


class EvaluateBatchResponse(BaseModel):
    """Response for batch job evaluation."""
    cv_id: str
    total_jobs: int
    matched_jobs: int
    results: List[EvaluationResult]


# ─── Document Schemas ──────────────────────────────────────────────────────

class GenerateDocumentsRequest(BaseModel):
    """Request to generate tailored CV and cover letter."""
    evaluation_id: str


class DocumentFile(BaseModel):
    """Info about a single generated file."""
    type: str  # cv_pdf, cv_docx, cl_pdf, cl_docx, ip_pdf, ip_docx
    filename: str
    download_url: str


class DocumentResponse(BaseModel):
    """Response with generated document details."""
    doc_id: str
    evaluation_id: str
    job_title: str
    company: str
    score: int
    files: List[DocumentFile]
    generated_at: datetime


# ─── Error Schemas ──────────────────────────────────────────────────────────

class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
