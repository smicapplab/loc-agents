import google.generativeai as genai
import os
import json
from typing import Dict, Any

class Reviewer:
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

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
        
        try:
            response = self.model.generate_content(prompt)
            content = response.text.strip()
            if content.startswith("```json"):
                content = content.replace("```json", "", 1).replace("```", "", 1).strip()
            
            evaluation = json.loads(content)
            job['evaluation'] = evaluation
            job['score'] = evaluation.get('score', 0)
            return job
        except Exception as e:
            print(f"Error reviewing job {job.get('title')}: {e}")
            job['score'] = 0
            job['evaluation'] = {"error": str(e)}
            return job
