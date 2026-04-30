# OpenAI Support & Project Consistency Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add OpenAI support to both projects and rename `job_filter` to `job-filter` for consistency.

**Architecture:** Use an inline abstraction (if/else) for LLM providers in existing service files. Consolidate project naming to kebab-case.

**Tech Stack:** Python, Google Generative AI, OpenAI SDK, Typer.

---

### Task 1: Project Renaming and Consistency

**Files:**
- Rename: `job_filter/` -> `job-filter/`
- Modify: `job-filter/main.py`
- Modify: `README.md`
- Modify: `.gitignore`

- [ ] **Step 1: Rename the directory**

Run: `mv job_filter job-filter`

- [ ] **Step 2: Update hardcoded paths in `job-filter/main.py`**

```python
# Change
profile_md_path = "job-seek/data/profile.md"
# (Wait, this is already correct, but I should check for any "job_filter" strings)
```

Run: `grep -r "job_filter" .`

- [ ] **Step 3: Update `.gitignore` and `README.md`**

Ensure all references use `job-filter`.

- [ ] **Step 4: Commit**

```bash
git add .
git commit -m "refactor: rename job_filter to job-filter for consistency"
```

### Task 2: Update Dependencies and Environment

**Files:**
- Modify: `job-seek/requirements.txt`
- Modify: `job-seek/.env.example`

- [ ] **Step 1: Add `openai` to requirements**

Add `openai` to `job-seek/requirements.txt`.

- [ ] **Step 2: Update `.env.example`**

```env
AI_PROVIDER=gemini
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o
GEMINI_MODEL=gemini-2.0-flash
```

- [ ] **Step 3: Commit**

```bash
git add job-seek/requirements.txt job-seek/.env.example
git commit -m "chore: add openai dependency and env vars"
```

### Task 3: Implement OpenAI Support in `src/core/reviewer.py`

**Files:**
- Modify: `src/core/reviewer.py`

- [ ] **Step 1: Update `Reviewer` class to support OpenAI**

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
        prompt = f"..." # (keep existing prompt)
        
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
            # ... (keep existing markdown cleaning)
        
        # ... (keep existing JSON parsing)
```

- [ ] **Step 2: Commit**

```bash
git add src/core/reviewer.py
git commit -m "feat: add openai support to Reviewer"
```

### Task 4: Implement OpenAI Support in `src/utils/pdf_processor.py`

**Files:**
- Modify: `src/utils/pdf_processor.py`

- [ ] **Step 1: Update `structure_resume` to support OpenAI**

Similar if/else logic for `AI_PROVIDER`.

- [ ] **Step 2: Commit**

```bash
git add src/utils/pdf_processor.py
git commit -m "feat: add openai support to pdf_processor"
```

### Task 5: Implement OpenAI Support in `job-filter/logic.py`

**Files:**
- Modify: `job-filter/logic.py`

- [ ] **Step 1: Update `extract_jobs_from_html` and `review_filtered_jobs`**

Use the same provider-based switching logic.

- [ ] **Step 2: Commit**

```bash
git add job-filter/logic.py
git commit -m "feat: add openai support to job-filter logic"
```

### Task 6: Verification

- [ ] **Step 1: Run `job-seek sync` with OpenAI**

`AI_PROVIDER=openai OPENAI_API_KEY=... python job-seek/main.py sync`

- [ ] **Step 2: Run `job-filter` with OpenAI**

`AI_PROVIDER=openai OPENAI_API_KEY=... python job-filter/main.py`
