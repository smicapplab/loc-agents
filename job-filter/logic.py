import os
import json
import google.generativeai as genai
from openai import OpenAI
from typing import List, Dict, Optional
from src.core.reviewer import Reviewer

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
    Uses an AI provider to extract a list of jobs from the email HTML content.
    """
    provider = os.getenv("AI_PROVIDER", "gemini").lower()
    
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

    if provider == "openai":
        try:
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            model_name = os.getenv("OPENAI_MODEL", "gpt-4o")
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            text = response.choices[0].message.content.strip()
            # OpenAI with response_format="json_object" might return a root object
            # if the prompt doesn't specify an array root.
            # But usually it follows instructions.
            data = json.loads(text)
            if isinstance(data, dict) and "jobs" in data:
                return data["jobs"]
            return data if isinstance(data, list) else []
        except Exception as e:
            print(f"Error extracting jobs with OpenAI: {e}")
            return []
    else:
        # Default to Gemini
        try:
            api_key = os.environ.get("GOOGLE_API_KEY")
            if not api_key:
                print("GOOGLE_API_KEY not found in environment")
                return []
            genai.configure(api_key=api_key)
            model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
            model = genai.GenerativeModel(model_name)
            
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
