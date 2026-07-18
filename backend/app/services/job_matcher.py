"""
Job Matcher Service — Orchestrates CV-to-job evaluation.
Refactored from the evaluation loop in the original main.py.
"""

from app.services.groq_client import get_match_score
from app.config import settings


def evaluate_single(cv_text: str, job: dict) -> dict:
    """
    Evaluate a single job against a CV and return the match result.

    Args:
        cv_text: Full text content of the candidate's CV.
        job: Dict with keys: title, company, location, link.

    Returns:
        dict with keys: score, reason, is_match.
    """
    title = job.get("title", "Unknown Title")
    company = job.get("company", "Unknown Company")
    location = job.get("location", "")
    link = job.get("link", "")

    result = get_match_score(cv_text, title, company, location, link)
    score = int(result.get("score", 0))
    reason = result.get("reason", "No reason provided.")
    is_match = score > settings.match_threshold

    return {
        "title": title,
        "company": company,
        "location": location,
        "link": link,
        "score": score,
        "reason": reason,
        "is_match": is_match,
    }


def evaluate_batch(cv_text: str, jobs: list[dict]) -> list[dict]:
    """
    Evaluate a list of jobs against a CV.

    Args:
        cv_text: Full text content of the candidate's CV.
        jobs: List of dicts, each with keys: title, company, location, link.

    Returns:
        List of result dicts, each with: title, company, location, link,
        score, reason, is_match.
    """
    results = []

    for job in jobs:
        try:
            result = evaluate_single(cv_text, job)
            results.append(result)
        except Exception as e:
            results.append({
                "title": job.get("title", "Unknown"),
                "company": job.get("company", "Unknown"),
                "location": job.get("location", ""),
                "link": job.get("link", ""),
                "score": 0,
                "reason": f"Evaluation error: {str(e)}",
                "is_match": False,
            })

    return results
