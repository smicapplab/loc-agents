# OpenAI Support Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add OpenAI as an alternative AI provider to the `Reviewer` class, controlled by the `AI_PROVIDER` environment variable.

**Architecture:** 
- Update `Reviewer.__init__` to handle `AI_PROVIDER` (defaulting to "gemini").
- Use `openai.OpenAI` client when provider is "openai".
- Use `google.generativeai` when provider is "gemini".
- Update `review_job` to branch logic based on the provider.

**Tech Stack:** Python, `openai`, `google-generativeai`, `pytest`, `unittest.mock`.

---

### Task 1: Create Unit Tests for Reviewer

**Files:**
- Create: `tests/test_reviewer.py`

- [ ] **Step 1: Write tests for Reviewer with Gemini (mocked)**

```python
import pytest
from unittest.mock import MagicMock, patch
import os
from src.core.reviewer import Reviewer

@pytest.mark.asyncio
@patch('src.core.reviewer.genai.GenerativeModel')
@patch.dict(os.environ, {"AI_PROVIDER": "gemini", "GOOGLE_API_KEY": "test_key"})
async def test_review_job_gemini(mock_model_class):
    mock_model = mock_model_class.return_value
    mock_response = MagicMock()
    mock_response.text = '{"score": 8, "reasoning": "Good match", "match_highlights": ["Python"], "concerns": []}'
    mock_model.generate_content.return_value = mock_response
    
    reviewer = Reviewer()
    job = {"title": "Python Dev", "company": "Test Co", "id": "123"}
    profile_md = "I know Python."
    
    result = await reviewer.review_job(job, profile_md)
    
    assert result['score'] == 8
    assert result['evaluation']['reasoning'] == "Good match"
    mock_model.generate_content.assert_called_once()

@pytest.mark.asyncio
@patch('src.core.reviewer.OpenAI')
@patch.dict(os.environ, {"AI_PROVIDER": "openai", "OPENAI_API_KEY": "test_key"})
async def test_review_job_openai(mock_openai_class):
    mock_client = mock_openai_class.return_value
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content='{"score": 9, "reasoning": "Great match", "match_highlights": ["AI"], "concerns": []}'))
    ]
    mock_client.chat.completions.create.return_value = mock_response
    
    reviewer = Reviewer()
    job = {"title": "AI Engineer", "company": "Test AI", "id": "456"}
    profile_md = "I know AI."
    
    result = await reviewer.review_job(job, profile_md)
    
    assert result['score'] == 9
    assert result['evaluation']['reasoning'] == "Great match"
    mock_client.chat.completions.create.assert_called_once()
```

- [ ] **Step 2: Run tests to verify Gemini passes (since it's already implemented) and OpenAI fails (since it's not)**

Run: `pytest tests/test_reviewer.py`
Expected: Gemini test might pass if existing code is compatible with mock, OpenAI test MUST fail.

### Task 2: Implement OpenAI Support in Reviewer

**Files:**
- Modify: `src/core/reviewer.py`

- [ ] **Step 1: Update imports and Reviewer class**

```python
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
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
        else:
            response = self.model.generate_content(prompt)
            content = response.text.strip()
            if content.startswith("```json"):
                content = content.replace("```json", "", 1).replace("```", "", 1).strip()
            
        try:
            evaluation = json.loads(content)
            job['evaluation'] = evaluation
            job['score'] = evaluation.get('score', 0)
            return job
        except Exception as e:
            print(f"Error reviewing job {job.get('title')}: {e}")
            job['score'] = 0
            job['evaluation'] = {"error": str(e)}
            return job
```

### Task 3: Verify and Commit

- [ ] **Step 1: Run all tests**

Run: `pytest tests/test_reviewer.py`
Expected: All tests PASS.

- [ ] **Step 2: Commit changes**

```bash
git add src/core/reviewer.py tests/test_reviewer.py
git commit -m "feat: add openai support to Reviewer"
```
