from __future__ import annotations
"""
Database models for the AI Job Match Agent.
Uses SQLModel (SQLAlchemy + Pydantic hybrid) for type-safe ORM models.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Text, JSON


# ─── CV Model ───────────────────────────────────────────────────────────────

class CV(SQLModel, table=True):
    """Stores uploaded CV data and extracted text."""

    __tablename__ = "cvs"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        index=True,
    )
    filename: str = Field(max_length=255)
    raw_text: str = Field(sa_column=Column(Text))
    char_count: int = Field(default=0)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    evaluations: List["Evaluation"] = Relationship(back_populates="cv")


# ─── Job Model ──────────────────────────────────────────────────────────────

class Job(SQLModel, table=True):
    """Stores job listing details."""

    __tablename__ = "jobs"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        index=True,
    )
    title: str = Field(max_length=500)
    company: str = Field(max_length=255)
    location: str = Field(max_length=500, default="")
    link: str = Field(max_length=2000, default="")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    evaluations: List["Evaluation"] = Relationship(back_populates="job")


# ─── Evaluation Model ──────────────────────────────────────────────────────

class Evaluation(SQLModel, table=True):
    """Stores the match score result for a CV evaluated against a job."""

    __tablename__ = "evaluations"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        index=True,
    )
    cv_id: str = Field(foreign_key="cvs.id", index=True)
    job_id: str = Field(foreign_key="jobs.id", index=True)
    score: int = Field(default=0)
    reason: str = Field(sa_column=Column(Text, default=""))
    is_match: bool = Field(default=False)
    evaluated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    cv: Optional[CV] = Relationship(back_populates="evaluations")
    job: Optional[Job] = Relationship(back_populates="evaluations")
    document: Optional["Document"] = Relationship(back_populates="evaluation")


# ─── Document Model ────────────────────────────────────────────────────────

class Document(SQLModel, table=True):
    """Stores generated tailored CV and cover letter file paths."""

    __tablename__ = "documents"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        index=True,
    )
    evaluation_id: str = Field(foreign_key="evaluations.id", unique=True, index=True)
    cv_pdf_path: str = Field(max_length=1000, default="")
    cv_docx_path: str = Field(max_length=1000, default="")
    cl_pdf_path: str = Field(max_length=1000, default="")
    cl_docx_path: str = Field(max_length=1000, default="")
    ip_pdf_path: str = Field(max_length=1000, default="")
    ip_docx_path: str = Field(max_length=1000, default="")
    tailored_data: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    evaluation: Optional[Evaluation] = Relationship(back_populates="document")
