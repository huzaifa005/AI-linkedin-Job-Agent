import os
import json
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()

def get_match_score(cv_text: str, job_title: str, company: str, location: str, url: str) -> dict:
    """
    Sends the CV text and job details to Groq API and returns a parsed dictionary
    containing the score and reasoning.
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set. Please set it in a .env file or your environment.")
    
    client = Groq(api_key=api_key)
    
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
    
    # We use llama-3.3-70b-versatile for high quality matching, with JSON mode enabled
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        model="llama-3.3-70b-versatile",
        response_format={"type": "json_object"},
        temperature=0.1,
        max_tokens=150
    )
    
    response_text = chat_completion.choices[0].message.content
    return json.loads(response_text)

def get_tailored_assets(cv_text: str, job_title: str, company: str, location: str, url: str) -> dict:
    """
    Sends the CV text and job details to Groq and asks it to return a tailored CV JSON
    and cover letter text. Strict constraint: no new details are invented.
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set. Please set it in a .env file or your environment.")
    
    client = Groq(api_key=api_key)
    
    system_prompt = (
        "You are an expert resume writer and recruiter.\n"
        "Your task is to review the candidate's CV and the job details, and produce tailored CV assets (profile, experience, projects, skills, tools) and a cover letter.\n"
        "CRITICAL INSTRUCTIONS:\n"
        "1. DO NOT invent, assume, or hallucinate any experience, skills, projects, certifications, or achievements. Only rephrase, reorganize, and emphasize information already present in the original CV.\n"
        "2. Ensure complete factual accuracy. If the job description asks for a skill the candidate doesn't have, do not add it.\n"
        "3. Highlight and prioritize the most relevant experience, projects, and skills for this target role.\n"
        "4. Return your entire response ONLY as a JSON object matching the schema below. Do not add any conversational text or markdown wrappers.\n\n"
        "JSON Schema:\n"
        "{\n"
        "  \"tailored_cv\": {\n"
        "    \"profile\": \"Brief tailored professional summary (approx. 3-4 sentences).\",\n"
        "    \"experience\": [\n"
        "      {\n"
        "        \"role\": \"Job Title from original CV (e.g. Senior Product Designer)\",\n"
        "        \"company\": \"Company Name from original CV\",\n"
        "        \"duration\": \"Duration from original CV\",\n"
        "        \"location\": \"Location from original CV\",\n"
        "        \"type\": \"Type from original CV\",\n"
        "        \"bullets\": [\n"
        "          \"Tailored bullet point emphasizing relevant experience using exact facts from CV.\",\n"
        "          \"Another tailored bullet point...\"\n"
        "        ]\n"
        "      }\n"
        "    ],\n"
        "    \"projects\": [\n"
        "      {\n"
        "        \"name\": \"Project Name from original CV\",\n"
        "        \"details\": \"Tailored project description using only facts from original CV.\"\n"
        "      }\n"
        "    ],\n"
        "    \"skills\": [\"Skill1\", \"Skill2\", \"...\"],\n"
        "    \"tools\": [\"Tool1\", \"Tool2\", \"...\"]\n"
        "  },\n"
        "  \"cover_letter\": {\n"
        "    \"date\": \"Current Date (e.g. July 16, 2026)\",\n"
        "    \"company\": \"Company name being applied to\",\n"
        "    \"letter_body\": \"The body of the cover letter addressed to the hiring manager. Emphasize matching experience without inventing details. Break into 3-4 short paragraphs.\"\n"
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
            {"role": "user", "content": user_prompt}
        ],
        model="llama-3.3-70b-versatile",
        response_format={"type": "json_object"},
        temperature=0.2,
        max_tokens=3000
    )
    
    response_text = chat_completion.choices[0].message.content
    return json.loads(response_text)

