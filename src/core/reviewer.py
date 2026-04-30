import google.generativeai as genai
from openai import OpenAI
import os
import json
from typing import Dict, Any

class Reviewer:
    def __init__(self, model_name: str = None):
        self.provider = os.getenv("AI_PROVIDER", "gemini").lower()
        if self.provider == "openai":
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            self.model_name = model_name or os.getenv("OPENAI_MODEL", "gpt-4o")
        else:
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY not found in environment")
            genai.configure(api_key=api_key)
            self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
            self.model = genai.GenerativeModel(self.model_name)

    async def review_job(self, job: Dict[str, Any], profile_md: str) -> Dict[str, Any]:
        """
        Scores a job based on its snippet/title and the user's profile.
        """
        prompt = f"""
        You are an expert technical recruiter. Score the following job listing against the candidate's profile.
        
        Candidate Profile (Markdown):
        {profile_md}
        
        Job Listing:
        Title: {job.get('title')}
        Company: {job.get('company')}
        Snippet/Summary: {job.get('posted_date', 'N/A')}
        
        Provide your evaluation in the following JSON format:
        {{
            "score": <integer from 0 to 10>,
            "reasoning": "<short explanation of why this score was given>",
            "match_highlights": ["<skill 1>", "<skill 2>"],
            "concerns": ["<missing skill 1>", "<location mismatch?>"]
        }}
        
        Return ONLY the JSON object.
        """
        
        if self.provider == "openai":
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"}
                )
                content = response.choices[0].message.content
            except Exception as e:
                print(f"OpenAI Error: {e}")
                job['score'] = 0
                job['evaluation'] = {"error": f"OpenAI Error: {str(e)}"}
                return job
        else:
            try:
                response = self.model.generate_content(prompt)
                content = response.text.strip()
                if content.startswith("```json"):
                    content = content.replace("```json", "", 1).replace("```", "", 1).strip()
            except Exception as e:
                print(f"Gemini Error: {e}")
                job['score'] = 0
                job['evaluation'] = {"error": f"Gemini Error: {str(e)}"}
                return job
            
        try:
            evaluation = json.loads(content)
            job['evaluation'] = evaluation
            job['score'] = evaluation.get('score', 0)
            return job
        except Exception as e:
            print(f"Error parsing JSON for job {job.get('title')}: {e}")
            job['score'] = 0
            job['evaluation'] = {"error": f"JSON Parse Error: {str(e)}", "content": content}
            return job
