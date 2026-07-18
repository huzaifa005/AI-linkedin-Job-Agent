"""
CV upload and retrieval endpoints.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlmodel import Session

from app.database import get_session
from app.models.models import CV
from app.schemas.schemas import CVUploadResponse, CVDetailResponse
from app.services.cv_parser import extract_text_from_pdf_bytes

router = APIRouter(prefix="/cv", tags=["CV"])


@router.post(
    "/upload",
    response_model=CVUploadResponse,
    summary="Upload CV PDF",
    description="Upload a PDF CV file. The text is extracted and stored for evaluation.",
)
async def upload_cv(
    file: UploadFile = File(..., description="PDF file of the candidate's CV"),
    session: Session = Depends(get_session),
):
    # Validate file type
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are accepted. Please upload a .pdf file.",
        )

    # Read file bytes
    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # Size limit: 10MB
    if len(file_bytes) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="File too large. Maximum size is 10MB.",
        )

    # Extract text
    try:
        raw_text = extract_text_from_pdf_bytes(file_bytes)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process PDF: {str(e)}",
        )

    # Save to database
    cv = CV(
        filename=file.filename,
        raw_text=raw_text,
        char_count=len(raw_text),
    )
    session.add(cv)
    session.commit()
    session.refresh(cv)

    return CVUploadResponse(
        cv_id=cv.id,
        filename=cv.filename,
        text_preview=raw_text[:500],
        char_count=cv.char_count,
        created_at=cv.created_at,
    )


@router.get(
    "/{cv_id}",
    response_model=CVDetailResponse,
    summary="Get CV Details",
    description="Retrieve the full parsed text and metadata for an uploaded CV.",
)
async def get_cv(cv_id: str, session: Session = Depends(get_session)):
    cv = session.get(CV, cv_id)
    if not cv:
        raise HTTPException(status_code=404, detail=f"CV not found: {cv_id}")

    return CVDetailResponse(
        cv_id=cv.id,
        filename=cv.filename,
        raw_text=cv.raw_text,
        char_count=cv.char_count,
        created_at=cv.created_at,
    )
