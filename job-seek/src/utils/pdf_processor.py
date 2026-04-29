import fitz
import google.generativeai as genai
import json
import os

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts text from a PDF file."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

def structure_resume(text: str) -> tuple[str, str]:
    """Structures resume text into MD and JSON using Gemini."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    prompt = f"""
    Analyze the following resume text and provide two separate sections:
    1. A professional persona in Markdown format (profile.md).
    2. A structured JSON requirements list (profile_index.json) with the following keys:
       - skills: list of strings
       - location_preference: string (Onsite, Hybrid, Remote, or Any)
       - seniority: string
       - target_job_titles: list of strings
       - years_of_experience: integer
    
    Return the response as a valid JSON object with two fields: "markdown" and "json_index".
    The "json_index" field should contain the actual JSON object for the requirements.
    
    Resume Text:
    {text}
    """
    
    response = model.generate_content(prompt)
    try:
        # Try to parse the response as a JSON object containing both parts
        # Gemini sometimes wraps JSON in code blocks
        content = response.text.strip()
        if content.startswith("```json"):
            content = content.replace("```json", "", 1).replace("```", "", 1).strip()
        
        data = json.loads(content)
        md_content = data.get("markdown", "")
        json_index = json.dumps(data.get("json_index", {}), indent=2)
        return md_content, json_index
    except Exception as e:
        # Fallback if Gemini doesn't follow the JSON format exactly
        return response.text, "{}"
