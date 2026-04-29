import os
import json
import google.generativeai as genai
from typing import List, Dict, Optional
from src.core.reviewer import Reviewer

# Configure Gemini
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

async def review_filtered_jobs(jobs: List[Dict], profile_md: str) -> List[Dict]:
    """
    Scores each filtered job using the shared Reviewer agent in parallel.
    """
    if not jobs:
        return []
        
    reviewer = Reviewer()
    scored_jobs = []
    
    for job in jobs:
        try:
            # Re-use existing review logic
            result = await reviewer.review_job(job, profile_md)
            if result.get('score', 0) >= 7:
                scored_jobs.append(result)
        except Exception as e:
            print(f"Error reviewing job {job.get('title')}: {e}")
            
    scored_jobs.sort(key=lambda x: x['score'], reverse=True)
    return scored_jobs

def filter_by_salary(job: Dict, min_salary: int = 250000) -> bool:
    """
    Filters a job by its salary. Returns True if salary >= min_salary or if salary is unknown.
    """
    salary = job.get('salary')
    if salary is None:
        return True
    
    try:
        salary_val = int(salary)
        return salary_val >= min_salary
    except (ValueError, TypeError):
        return True

def extract_jobs_from_html(html_content: str) -> List[Dict]:
    """
    Uses Gemini to extract a list of jobs from the email HTML content.
    """
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    prompt = f"""
    Extract a list of job listings from the following email HTML. 
    For each job, extract:
    - title
    - company
    - link (if available)
    - salary (as a single integer, e.g., 250000. If a range is given, use the lower bound. If not mentioned, use null)
    - location (if available)

    Return ONLY a valid JSON list of objects.
    
    Email HTML:
    {html_content}
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:-3].strip()
        elif text.startswith("```"):
            text = text[3:-3].strip()
            
        return json.loads(text)
    except Exception as e:
        print(f"Error extracting jobs with Gemini: {e}")
        return []
