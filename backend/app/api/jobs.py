"""
Job evaluation endpoints — single and batch evaluation against a CV.
"""

import os
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select

from app.database import get_session
from app.config import settings
from app.models.models import CV, Job, Evaluation, Document
from app.schemas.schemas import (
    EvaluateSingleRequest,
    EvaluateSingleResponse,
    EvaluateBatchRequest,
    EvaluateBatchResponse,
    EvaluationResult,
)
from app.services.job_matcher import evaluate_single, evaluate_batch
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

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post(
    "/evaluate-single",
    response_model=EvaluateSingleResponse,
    summary="Evaluate Single Job",
    description="Evaluate a single job listing against an uploaded CV. Returns the match score and reasoning in real-time.",
)
async def evaluate_single_job(
    request: EvaluateSingleRequest,
    session: Session = Depends(get_session),
):
    # Get the CV
    cv = session.get(CV, request.cv_id)
    if not cv:
        raise HTTPException(status_code=404, detail=f"CV not found: {request.cv_id}")

    # Check if job already exists in database
    job = None
    if request.job.link:
        job = session.exec(select(Job).where(Job.link == request.job.link)).first()
    if not job:
        job = session.exec(
            select(Job).where(Job.title == request.job.title, Job.company == request.job.company)
        ).first()

    if not job:
        job = Job(
            title=request.job.title,
            company=request.job.company,
            location=request.job.location,
            link=request.job.link,
        )
        session.add(job)
        session.commit()
        session.refresh(job)

    # Evaluate
    try:
        result = evaluate_single(
            cv_text=cv.raw_text,
            job={
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "link": job.link,
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Evaluation failed: {str(e)}",
        )

    # Save evaluation
    evaluation = Evaluation(
        cv_id=cv.id,
        job_id=job.id,
        score=result["score"],
        reason=result["reason"],
        is_match=result["is_match"],
    )
    session.add(evaluation)
    session.commit()
    session.refresh(evaluation)

    doc_id = None
    if evaluation.is_match:
        try:
            assets = get_tailored_assets(
                cv_text=cv.raw_text,
                job_title=job.title,
                company=job.company,
                location=job.location,
                url=job.link,
            )
            tailored_cv_data = assets.get("tailored_cv", {})
            cover_letter_data = assets.get("cover_letter", {})
            interview_prep_data = assets.get("interview_prep", {})
            interview_prep_data["company"] = job.company
            interview_prep_data["role"] = job.title

            folder_name = sanitize_folder_name(f"{job.company}_{job.title}")
            target_dir = os.path.join(settings.storage_path, folder_name)
            os.makedirs(target_dir, exist_ok=True)

            cv_docx_path = os.path.join(target_dir, "tailored_cv.docx")
            cv_pdf_path = os.path.join(target_dir, "tailored_cv.pdf")
            cl_docx_path = os.path.join(target_dir, "cover_letter.docx")
            cl_pdf_path = os.path.join(target_dir, "cover_letter.pdf")
            ip_docx_path = os.path.join(target_dir, "interview_prep.docx")
            ip_pdf_path = os.path.join(target_dir, "interview_prep.pdf")

            generate_cv_docx(tailored_cv_data, cv_docx_path)
            generate_cv_pdf(tailored_cv_data, cv_pdf_path)
            generate_cover_letter_docx(cover_letter_data, cl_docx_path)
            generate_cover_letter_pdf(cover_letter_data, cl_pdf_path)
            generate_interview_prep_docx(interview_prep_data, ip_docx_path)
            generate_interview_prep_pdf(interview_prep_data, ip_pdf_path)

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
            doc_id = doc.id
        except Exception as e:
            print(f"Failed to generate documents automatically for {job.title}: {str(e)}")

    return EvaluateSingleResponse(
        result=EvaluationResult(
            evaluation_id=evaluation.id,
            job_title=job.title,
            company=job.company,
            location=job.location,
            link=job.link,
            score=evaluation.score,
            reason=evaluation.reason,
            is_match=evaluation.is_match,
            documents_available=evaluation.is_match and doc_id is not None,
            doc_id=doc_id,
        )
    )


@router.post(
    "/evaluate-batch",
    response_model=EvaluateBatchResponse,
    summary="Evaluate Batch Jobs",
    description="Evaluate multiple job listings against an uploaded CV. Processes each job sequentially and returns all results.",
)
async def evaluate_batch_jobs(
    request: EvaluateBatchRequest,
    session: Session = Depends(get_session),
):
    # Get the CV
    cv = session.get(CV, request.cv_id)
    if not cv:
        raise HTTPException(status_code=404, detail=f"CV not found: {request.cv_id}")

    evaluation_results = []
    matched_count = 0

    for job_input in request.jobs:
        # Check if job already exists in database
        job = None
        if job_input.link:
            job = session.exec(select(Job).where(Job.link == job_input.link)).first()
        if not job:
            job = session.exec(
                select(Job).where(Job.title == job_input.title, Job.company == job_input.company)
            ).first()

        if not job:
            job = Job(
                title=job_input.title,
                company=job_input.company,
                location=job_input.location,
                link=job_input.link,
            )
            session.add(job)
            session.commit()
            session.refresh(job)

        # Evaluate
        try:
            result = evaluate_single(
                cv_text=cv.raw_text,
                job={
                    "title": job.title,
                    "company": job.company,
                    "location": job.location,
                    "link": job.link,
                },
            )
        except Exception as e:
            result = {
                "score": 0,
                "reason": f"Error: {str(e)}",
                "is_match": False,
            }

        # Save evaluation
        evaluation = Evaluation(
            cv_id=cv.id,
            job_id=job.id,
            score=result["score"],
            reason=result["reason"],
            is_match=result["is_match"],
        )
        session.add(evaluation)
        session.commit()
        session.refresh(evaluation)

        doc_id = None
        if evaluation.is_match:
            matched_count += 1
            try:
                assets = get_tailored_assets(
                    cv_text=cv.raw_text,
                    job_title=job.title,
                    company=job.company,
                    location=job.location,
                    url=job.link,
                )
                tailored_cv_data = assets.get("tailored_cv", {})
                cover_letter_data = assets.get("cover_letter", {})
                interview_prep_data = assets.get("interview_prep", {})
                interview_prep_data["company"] = job.company
                interview_prep_data["role"] = job.title

                folder_name = sanitize_folder_name(f"{job.company}_{job.title}")
                target_dir = os.path.join(settings.storage_path, folder_name)
                os.makedirs(target_dir, exist_ok=True)

                cv_docx_path = os.path.join(target_dir, "tailored_cv.docx")
                cv_pdf_path = os.path.join(target_dir, "tailored_cv.pdf")
                cl_docx_path = os.path.join(target_dir, "cover_letter.docx")
                cl_pdf_path = os.path.join(target_dir, "cover_letter.pdf")
                ip_docx_path = os.path.join(target_dir, "interview_prep.docx")
                ip_pdf_path = os.path.join(target_dir, "interview_prep.pdf")

                generate_cv_docx(tailored_cv_data, cv_docx_path)
                generate_cv_pdf(tailored_cv_data, cv_pdf_path)
                generate_cover_letter_docx(cover_letter_data, cl_docx_path)
                generate_cover_letter_pdf(cover_letter_data, cl_pdf_path)
                generate_interview_prep_docx(interview_prep_data, ip_docx_path)
                generate_interview_prep_pdf(interview_prep_data, ip_pdf_path)

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
                doc_id = doc.id
            except Exception as e:
                print(f"Failed to generate documents automatically for {job.title}: {str(e)}")

        evaluation_results.append(
            EvaluationResult(
                evaluation_id=evaluation.id,
                job_title=job.title,
                company=job.company,
                location=job.location,
                link=job.link,
                score=evaluation.score,
                reason=evaluation.reason,
                is_match=evaluation.is_match,
                documents_available=evaluation.is_match and doc_id is not None,
                doc_id=doc_id,
            )
        )

    return EvaluateBatchResponse(
        cv_id=cv.id,
        total_jobs=len(request.jobs),
        matched_jobs=matched_count,
        results=evaluation_results,
    )
