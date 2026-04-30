import fitz
import google.generativeai as genai
from openai import OpenAI
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
    """Structures resume text into MD and JSON using AI provider."""
    provider = os.getenv("AI_PROVIDER", "gemini").lower()
    
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

    if provider == "openai":
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        model_name = os.getenv("OPENAI_MODEL", "gpt-4o")
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI Error: {e}")
            return f"Error: {str(e)}", "{}"
    else:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        
        genai.configure(api_key=api_key)
        model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        model = genai.GenerativeModel(model_name)
        
        try:
            response = model.generate_content(prompt)
            content = response.text.strip()
            if content.startswith("```json"):
                content = content.replace("```json", "", 1).replace("```", "", 1).strip()
        except Exception as e:
            print(f"Gemini Error: {e}")
            return f"Error: {str(e)}", "{}"
    
    try:
        data = json.loads(content)
        md_content = data.get("markdown", "")
        json_index = json.dumps(data.get("json_index", {}), indent=2)
        return md_content, json_index
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        return content, "{}"
