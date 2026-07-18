import os
import json
import sys
import re
from pypdf import PdfReader
from groq_client import get_match_score, get_tailored_assets
from doc_generator import (
    generate_cv_docx,
    generate_cover_letter_docx,
    generate_cv_pdf,
    generate_cover_letter_pdf
)

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts text from a given PDF file path."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found at: {pdf_path}")
    
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text.strip()

def sanitize_folder_name(name: str) -> str:
    """Sanitizes string to be a safe folder name on Windows/Linux."""
    # Keep only alphanumeric characters, spaces, and underscores
    sanitized = re.sub(r'[^a-zA-Z0-9\s_-]', '', name)
    # Replace spaces with underscores
    sanitized = re.sub(r'\s+', '_', sanitized)
    return sanitized.strip('_')

def main():
    # File paths
    cv_pdf_path = "Huzaifa Naeem CV Senior Product Designer.pdf"
    jobs_json_path = "london_remote_product_designers.json"
    
    # 1. Convert PDF CV to text
    print(f"Reading CV from '{cv_pdf_path}'...")
    try:
        cv_text = extract_text_from_pdf(cv_pdf_path)
        print(f"Successfully extracted {len(cv_text)} characters from CV.")
    except Exception as e:
        print(f"Error reading PDF CV: {e}", file=sys.stderr)
        sys.exit(1)
        
    # 2. Read jobs JSON
    print(f"Reading jobs from '{jobs_json_path}'...")
    if not os.path.exists(jobs_json_path):
        print(f"Error: Jobs JSON file not found at '{jobs_json_path}'. Did you run the scraper first?", file=sys.stderr)
        sys.exit(1)
        
    with open(jobs_json_path, 'r', encoding='utf-8') as f:
        try:
            jobs = json.load(f)
        except Exception as e:
            print(f"Error parsing jobs JSON: {e}", file=sys.stderr)
            sys.exit(1)
            
    print(f"Evaluating {len(jobs)} jobs...")
    print("-" * 60)
    
    results = []
    matched_titles = []
    
    # Ensure outputs directory exists
    os.makedirs("outputs", exist_ok=True)
    
    # 3. Loop over job details
    for idx, job in enumerate(jobs, 1):
        title = job.get("title", "Unknown Title")
        company = job.get("company", "Unknown Company")
        location = job.get("location", "Unknown Location")
        url = job.get("link", "")
        
        print(f"[{idx}/{len(jobs)}] Evaluating: {title} at {company}...")
        try:
            res = get_match_score(cv_text, title, company, location, url)
            score = int(res.get("score", 0))
            reason = res.get("reason", "No reason provided.")
            
            results.append({
                "title": title,
                "company": company,
                "score": score,
                "reason": reason
            })
            
            # If score is above 6, print title and generate tailored outputs
            if score > 6:
                matched_titles.append(title)
                print(f"  -> Score: {score}/18 (> 6). Generating tailored assets...")
                
                # Sanitize names for path
                folder_name = sanitize_folder_name(f"{company}_{title}")
                target_dir = os.path.join("outputs", folder_name)
                os.makedirs(target_dir, exist_ok=True)
                
                # Generate tailored CV and Cover Letter JSON data from Groq
                assets = get_tailored_assets(cv_text, title, company, location, url)
                
                tailored_cv_data = assets.get("tailored_cv", {})
                cover_letter_data = assets.get("cover_letter", {})
                
                # Output file paths
                cv_docx_path = os.path.join(target_dir, "tailored_cv.docx")
                cv_pdf_path = os.path.join(target_dir, "tailored_cv.pdf")
                cl_docx_path = os.path.join(target_dir, "cover_letter.docx")
                cl_pdf_path = os.path.join(target_dir, "cover_letter.pdf")
                
                # Render files
                generate_cv_docx(tailored_cv_data, cv_docx_path)
                generate_cv_pdf(tailored_cv_data, cv_pdf_path)
                generate_cover_letter_docx(cover_letter_data, cl_docx_path)
                generate_cover_letter_pdf(cover_letter_data, cl_pdf_path)
                
                print(f"  -> Saved assets in: {target_dir}")
                
        except Exception as e:
            print(f"  Error evaluating job {title}: {e}", file=sys.stderr)
            results.append({
                "title": title,
                "company": company,
                "score": 0,
                "reason": f"Error: {e}"
            })
            
    # 4. Print results to terminal
    print("\n" + "=" * 60)
    print("JOB MATCH EVALUATION SUMMARY")
    print("=" * 60)
    for res in results:
        print(f"Job: {res['title']} ({res['company']})")
        print(f"Score: {res['score']}/18")
        print(f"Reason: {res['reason']}")
        print("-" * 60)
        
    print("\n" + "=" * 60)
    print("MATCHED JOB TITLES (Score > 6)")
    print("=" * 60)
    if matched_titles:
        for title in matched_titles:
            print(f"- {title}")
    else:
        print("No jobs matched with a score above 6.")
    print("=" * 60)

if __name__ == "__main__":
    main()
