"""
Document generation and download endpoints.
"""

import os
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlmodel import Session

from app.database import get_session
from app.config import settings
from app.models.models import CV, Evaluation, Job, Document
from app.schemas.schemas import (
    GenerateDocumentsRequest,
    DocumentResponse,
    DocumentFile,
)
from app.services.groq_client import get_tailored_assets
from app.services.doc_generator import (
    generate_cv_docx,
    generate_cv_pdf,
    generate_cover_letter_docx,
    generate_cover_letter_pdf,
    generate_interview_prep_docx,
    generate_interview_prep_pdf,
)
from app.utils.file_helpers import sanitize_folder_name

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post(
    "/generate",
    response_model=DocumentResponse,
    summary="Generate Tailored Documents",
    description="Generate a tailored CV and cover letter for a matched job evaluation. Creates DOCX and PDF versions.",
)
async def generate_documents(
    request: GenerateDocumentsRequest,
    session: Session = Depends(get_session),
):
    # Get the evaluation
    evaluation = session.get(Evaluation, request.evaluation_id)
    if not evaluation:
        raise HTTPException(
            status_code=404,
            detail=f"Evaluation not found: {request.evaluation_id}",
        )

    # Check if documents already exist
    if evaluation.document:
        doc = evaluation.document
        return _build_document_response(doc, evaluation)

    # Get the CV and Job
    cv = session.get(CV, evaluation.cv_id)
    job = session.get(Job, evaluation.job_id)
    if not cv or not job:
        raise HTTPException(status_code=404, detail="Associated CV or Job not found.")

    # Generate tailored assets from Groq
    try:
        assets = get_tailored_assets(
            cv_text=cv.raw_text,
            job_title=job.title,
            company=job.company,
            location=job.location,
            url=job.link,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate tailored assets: {str(e)}",
        )

    tailored_cv_data = assets.get("tailored_cv", {})
    cover_letter_data = assets.get("cover_letter", {})
    interview_prep_data = assets.get("interview_prep", {})
    # Inject job metadata into interview prep data
    interview_prep_data["company"] = job.company
    interview_prep_data["role"] = job.title

    # Create output directory
    folder_name = sanitize_folder_name(f"{job.company}_{job.title}")
    target_dir = os.path.join(settings.storage_path, folder_name)
    os.makedirs(target_dir, exist_ok=True)

    # Generate all 6 document formats
    cv_docx_path = os.path.join(target_dir, "tailored_cv.docx")
    cv_pdf_path = os.path.join(target_dir, "tailored_cv.pdf")
    cl_docx_path = os.path.join(target_dir, "cover_letter.docx")
    cl_pdf_path = os.path.join(target_dir, "cover_letter.pdf")
    ip_docx_path = os.path.join(target_dir, "interview_prep.docx")
    ip_pdf_path = os.path.join(target_dir, "interview_prep.pdf")

    try:
        generate_cv_docx(tailored_cv_data, cv_docx_path)
        generate_cv_pdf(tailored_cv_data, cv_pdf_path)
        generate_cover_letter_docx(cover_letter_data, cl_docx_path)
        generate_cover_letter_pdf(cover_letter_data, cl_pdf_path)
        generate_interview_prep_docx(interview_prep_data, ip_docx_path)
        generate_interview_prep_pdf(interview_prep_data, ip_pdf_path)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate documents: {str(e)}",
        )

    # Save document record
    doc = Document(
        evaluation_id=evaluation.id,
        cv_pdf_path=cv_pdf_path,
        cv_docx_path=cv_docx_path,
        cl_pdf_path=cl_pdf_path,
        cl_docx_path=cl_docx_path,
        ip_pdf_path=ip_pdf_path,
        ip_docx_path=ip_docx_path,
        tailored_data=assets,
    )
    session.add(doc)
    session.commit()
    session.refresh(doc)

    return _build_document_response(doc, evaluation)


@router.get(
    "/{doc_id}",
    response_model=DocumentResponse,
    summary="Get Document Status",
    description="Get the status and download links for generated documents.",
)
async def get_document(doc_id: str, session: Session = Depends(get_session)):
    doc = session.get(Document, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document not found: {doc_id}")

    evaluation = session.get(Evaluation, doc.evaluation_id)
    return _build_document_response(doc, evaluation)


@router.get(
    "/{doc_id}/download/{file_type}",
    summary="Download Document",
    description="Download a specific generated document. Valid types: cv_pdf, cv_docx, cl_pdf, cl_docx",
)
async def download_document(
    doc_id: str,
    file_type: str,
    session: Session = Depends(get_session),
):
    doc = session.get(Document, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document not found: {doc_id}")

    # Map file type to path and content type
    file_map = {
        "cv_pdf": (doc.cv_pdf_path, "application/pdf", "tailored_cv.pdf"),
        "cv_docx": (
            doc.cv_docx_path,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "tailored_cv.docx",
        ),
        "cl_pdf": (doc.cl_pdf_path, "application/pdf", "cover_letter.pdf"),
        "cl_docx": (
            doc.cl_docx_path,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "cover_letter.docx",
        ),
        "ip_pdf": (doc.ip_pdf_path, "application/pdf", "interview_prep.pdf"),
        "ip_docx": (
            doc.ip_docx_path,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "interview_prep.docx",
        ),
    }

    if file_type not in file_map:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file_type}. Must be one of: {', '.join(file_map.keys())}",
        )

    file_path, content_type, filename = file_map[file_type]

    if not file_path or not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail=f"File not found on disk. It may have been cleaned up.",
        )

    def iter_file():
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                yield chunk

    return StreamingResponse(
        iter_file(),
        media_type=content_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


def _build_document_response(doc: Document, evaluation: Evaluation) -> DocumentResponse:
    """Helper to build a consistent DocumentResponse."""
    base_url = f"/api/documents/{doc.id}/download"
    files = []

    if doc.cv_pdf_path:
        files.append(DocumentFile(type="cv_pdf", filename="tailored_cv.pdf", download_url=f"{base_url}/cv_pdf"))
    if doc.cv_docx_path:
        files.append(DocumentFile(type="cv_docx", filename="tailored_cv.docx", download_url=f"{base_url}/cv_docx"))
    if doc.cl_pdf_path:
        files.append(DocumentFile(type="cl_pdf", filename="cover_letter.pdf", download_url=f"{base_url}/cl_pdf"))
    if doc.cl_docx_path:
        files.append(DocumentFile(type="cl_docx", filename="cover_letter.docx", download_url=f"{base_url}/cl_docx"))
    if doc.ip_pdf_path:
        files.append(DocumentFile(type="ip_pdf", filename="interview_prep.pdf", download_url=f"{base_url}/ip_pdf"))
    if doc.ip_docx_path:
        files.append(DocumentFile(type="ip_docx", filename="interview_prep.docx", download_url=f"{base_url}/ip_docx"))

    # Get the job info from evaluation
    job_title = ""
    company = ""
    if evaluation and evaluation.job:
        job_title = evaluation.job.title
        company = evaluation.job.company

    return DocumentResponse(
        doc_id=doc.id,
        evaluation_id=doc.evaluation_id,
        job_title=job_title,
        company=company,
        score=evaluation.score if evaluation else 0,
        files=files,
        generated_at=doc.generated_at,
    )
