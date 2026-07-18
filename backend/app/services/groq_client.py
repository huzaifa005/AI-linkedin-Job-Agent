"""
Groq LLM Client Service — Handles all LLM interactions.
Refactored from the original groq_client.py to use injected configuration
instead of reading os.environ directly.
"""

import json
from groq import Groq
from app.config import settings


def _get_client() -> Groq:
    """Creates a Groq client instance using configured API key."""
    if not settings.groq_api_key:
        raise ValueError(
            "GROQ_API_KEY is not configured. "
            "Please set it in the .env file or environment variables."
        )
    return Groq(api_key=settings.groq_api_key)


def get_match_score(
    cv_text: str,
    job_title: str,
    company: str,
    location: str,
    url: str,
) -> dict:
    """
    Sends the CV text and job details to Groq API and returns a parsed
    dictionary containing the match score and reasoning.

    Args:
        cv_text: Full text content of the candidate's CV.
        job_title: Title of the job listing.
        company: Company name.
        location: Job location.
        url: Job listing URL.

    Returns:
        dict with keys: 'score' (int 8-18), 'reason' (str).
    """
    client = _get_client()

    system_prompt = (
        "You are an expert technical recruiter assessing candidate fit.\n"
        "Compare the candidate's CV to the provided job details.\n"
        "Assign a fit score strictly between 8 and 18 (inclusive), where 8 represents a complete mismatch/poor fit "
        "and 18 represents an exceptional, perfect match.\n"
        "Return your response ONLY as a JSON object with 'score' (integer between 8 and 18) "
        "and 'reason' (a 1-sentence concise explanation). Do not add any extra text or conversational filler.\n"
        "JSON format:\n"
        '{"score": 12, "reason": "Brief explanation of the score."}'
    )

    job_details = (
        f"Job Title: {job_title}\n"
        f"Company: {company}\n"
        f"Location: {location}\n"
        f"URL: {url}\n"
    )

    user_prompt = (
        f"--- CANDIDATE CV ---\n"
        f"{cv_text}\n\n"
        f"--- JOB DETAILS ---\n"
        f"{job_details}"
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        model=settings.groq_model,
        response_format={"type": "json_object"},
        temperature=settings.groq_match_temperature,
        max_tokens=settings.groq_match_max_tokens,
    )

    response_text = chat_completion.choices[0].message.content
    return json.loads(response_text)


def get_tailored_assets(
    cv_text: str,
    job_title: str,
    company: str,
    location: str,
    url: str,
) -> dict:
    """
    Sends the CV text and job details to Groq and returns a tailored CV JSON,
    cover letter text, and interview preparation guide. Strict constraint: no new details are invented.

    Args:
        cv_text: Full text content of the candidate's CV.
        job_title: Title of the job listing.
        company: Company name.
        location: Job location.
        url: Job listing URL.

    Returns:
        dict with keys: 'tailored_cv' (dict), 'cover_letter' (dict), 'interview_prep' (dict).
    """
    client = _get_client()

    system_prompt = (
        "You are an expert resume writer, recruiter, and interview coach.\n"
        "Your task is to review the candidate's CV and the job details, and produce tailored CV assets "
        "(profile, experience, projects, skills, tools), a cover letter, and an interview preparation guide.\n"
        "CRITICAL INSTRUCTIONS:\n"
        "1. DO NOT invent, assume, or hallucinate any experience, skills, projects, certifications, or achievements "
        "not present in the original CV. Only rephrase, reorganize, and emphasize information already present in the original CV.\n"
        "2. Ensure complete factual accuracy. If the job description asks for a skill the candidate doesn't have, "
        "do not add it to the CV, but you can mention key topics to study in the interview prep.\n"
        "3. Highlight and prioritize the most relevant experience, projects, and skills for this target role.\n"
        "4. Return your entire response ONLY as a JSON object matching the schema below. "
        "Do not add any conversational text or markdown wrappers.\n\n"
        "JSON Schema:\n"
        "{\n"
        '  "tailored_cv": {\n'
        '    "profile": "Brief tailored professional summary (approx. 3-4 sentences).",\n'
        '    "experience": [\n'
        "      {\n"
        '        "role": "Job Title from original CV (e.g. Senior Product Designer)",\n'
        '        "company": "Company Name from original CV",\n'
        '        "duration": "Duration from original CV",\n'
        '        "location": "Location from original CV",\n'
        '        "type": "Type from original CV",\n'
        '        "bullets": [\n'
        '          "Tailored bullet point emphasizing relevant experience using exact facts from CV.",\n'
        '          "Another tailored bullet point..."\n'
        "        ]\n"
        "      }\n"
        "    ],\n"
        '    "projects": [\n'
        "      {\n"
        '        "name": "Project Name from original CV",\n'
        '        "details": "Tailored project description using only facts from original CV."\n'
        "      }\n"
        "    ],\n"
        '    "skills": ["Skill1", "Skill2", "..."],\n'
        '    "tools": ["Tool1", "Tool2", "..."]\n'
        '  },\n'
        '  "cover_letter": {\n'
        '    "date": "Current Date (e.g. July 16, 2026)",\n'
        '    "company": "Company name being applied to",\n'
        '    "letter_body": "The body of the cover letter addressed to the hiring manager. '
        'Emphasize matching experience without inventing details. Break into 3-4 short paragraphs."\n'
        '  },\n'
        '  "interview_prep": {\n'
        '    "company_research": "Brief research overview of the company, what they do, their industry focus, and how this role fits in.",\n'
        '    "role_prep_notes": "Preparation notes and strategies specific to this role (e.g. key focus areas to emphasize during discussions).",\n'
        '    "key_topics": ["Topic to study/prepare 1", "Topic to study/prepare 2", "Topic to study/prepare 3"],\n'
        '    "likely_questions": [\n'
        "      {\n"
        '        "question": "An interview question likely to be asked for this role.",\n'
        '        "suggested_answer": "A suggested answer or talking points using facts from candidate\'s CV."\n'
        "      },\n"
        "      {\n"
        '        "question": "Another likely interview question.",\n'
        '        "suggested_answer": "Suggested answer/talking points."\n'
        "      },\n"
        "      {\n"
        '        "question": "A third likely interview question.",\n'
        '        "suggested_answer": "Suggested answer/talking points."\n'
        "      }\n"
        "    ]\n"
        "  }\n"
        "}"
    )

    job_details = (
        f"Job Title: {job_title}\n"
        f"Company: {company}\n"
        f"Location: {location}\n"
        f"URL: {url}\n"
    )

    user_prompt = (
        f"--- CANDIDATE CV ---\n"
        f"{cv_text}\n\n"
        f"--- JOB DETAILS ---\n"
        f"{job_details}"
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        model=settings.groq_model,
        response_format={"type": "json_object"},
        temperature=settings.groq_assets_temperature,
        max_tokens=settings.groq_assets_max_tokens,
    )

    response_text = chat_completion.choices[0].message.content
    return json.loads(response_text)
