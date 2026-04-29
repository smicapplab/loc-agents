# PH Job-Seek AI Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an autonomous AI agent that scrapes job boards in the Philippines, filters them using a resume profile, deduplicates via SQLite, and sends a single aggregated email.

**Architecture:** Decoupled system with a Resume Pre-processor and a Job Searching Agent. Uses LangGraph for orchestration, Crawl4AI for parallel scraping, and SQLite for persistence.

**Tech Stack:** Python 3.11+, LangGraph, Crawl4AI, Gemini 2.0 Flash, SQLite, FastAPI, Typer, PyMuPDF.

---

### Task 1: Environment & Base Setup

**Files:**
- Create: `job-seek/requirements.txt`
- Create: `job-seek/.env.example`

- [ ] **Step 1: Define dependencies**

```text
fastapi
uvicorn
typer
langgraph
crawl4ai
google-generativeai
pymupdf
pydantic
pydantic-settings
python-dotenv
resend
aiosqlite
pytest
pytest-asyncio
```

- [ ] **Step 2: Create .env.example**

```text
GOOGLE_API_KEY=your_gemini_api_key
RESEND_API_KEY=your_resend_api_key
EMAIL_TO=your_email@example.com
EMAIL_FROM=onboarding@resend.dev
```

- [ ] **Step 3: Commit setup**

```bash
git add job-seek/requirements.txt job-seek/.env.example
git commit -m "chore: initial project setup and dependencies"
```

---

### Task 2: Resume Processor (PDF to MD/JSON)

**Files:**
- Create: `job-seek/src/utils/pdf_processor.py`
- Test: `job-seek/tests/test_pdf_processor.py`

- [ ] **Step 1: Write test for PDF extraction**

```python
import pytest
from src.utils.pdf_processor import extract_text_from_pdf

def test_extract_text_from_pdf():
    # Assumes a dummy pdf exists or we mock it
    text = extract_text_from_pdf("data/resume.pdf")
    assert len(text) > 0
```

- [ ] **Step 2: Implement extraction logic**

```python
import fitz

def extract_text_from_pdf(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text
```

- [ ] **Step 3: Implement Gemini Structuring**

```python
import google.generativeai as genai
import json

def structure_resume(text: str):
    model = genai.GenerativeModel('gemini-2.0-flash')
    prompt = f"Convert this resume to a professional Markdown persona and a structured JSON requirements list (skills, location, seniority, job_titles).\n\nResume:\n{text}"
    response = model.generate_content(prompt)
    # Logic to split response into MD and JSON
    return response.text
```

- [ ] **Step 4: Commit processor**

```bash
git add job-seek/src/utils/pdf_processor.py
git commit -m "feat: add resume pdf processor and gemini structuring"
```

---

### Task 3: SQLite Persistence Layer

**Files:**
- Create: `job-seek/src/utils/db.py`

- [ ] **Step 1: Implement Database initialization**

```python
import aiosqlite

DB_PATH = "data/jobs.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                title TEXT,
                company TEXT,
                link TEXT,
                posted_date TEXT,
                date_emailed TEXT
            )
        """)
        await db.commit()
```

- [ ] **Step 2: Implement Check/Save logic**

```python
async def job_exists(job_id: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT 1 FROM jobs WHERE id = ?", (job_id,)) as cursor:
            return await cursor.fetchone() is not None

async def save_job(job_data: dict):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO jobs (id, title, company, link, posted_date, date_emailed) VALUES (?, ?, ?, ?, ?, ?)",
            (job_data['id'], job_data['title'], job_data['company'], job_data['link'], job_data['posted_date'], job_data['date_emailed'])
        )
        await db.commit()
```

- [ ] **Step 3: Commit DB module**

```bash
git add job-seek/src/utils/db.py
git commit -m "feat: add sqlite persistence for deduplication"
```

---

### Task 4: Parallel Scrapers (Crawl4AI)

**Files:**
- Create: `job-seek/src/scrapers/base.py`
- Create: `job-seek/src/scrapers/linkedin.py`
- Create: `job-seek/src/scrapers/seek.py`

- [ ] **Step 1: Implement Base Scraper with Crawl4AI**

```python
from crawl4ai import AsyncWebCrawler

class BaseScraper:
    async def scrape(self, url: str):
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=url)
            return result.markdown
```

- [ ] **Step 2: Implement parallel runner in Orchestrator**

```python
import asyncio

async def run_parallel_scrapes(queries: list):
    tasks = [linkedin_scraper.scrape(q) for q in queries]
    results = await asyncio.gather(*tasks)
    return results
```

- [ ] **Step 3: Commit scrapers**

```bash
git add job-seek/src/scrapers/
git commit -m "feat: implement parallel scrapers using Crawl4AI"
```

---

### Task 4: Reviewer Sub-Agent (LangGraph)

**Files:**
- Create: `job-seek/src/agents/reviewer.py`
- Create: `job-seek/src/agents/graph.py`

- [ ] **Step 1: Define Reviewer Logic**

```python
def review_job(job_content, profile_md):
    model = genai.GenerativeModel('gemini-2.0-flash')
    prompt = f"Score this job from 0-10 based on compatibility with this profile. Explain why.\n\nProfile: {profile_md}\n\nJob: {job_content}"
    # ... return score and summary
```

- [ ] **Step 2: Build LangGraph Workflow**

```python
from langgraph.graph import StateGraph, END

workflow = StateGraph(JobState)
workflow.add_node("scrape", scrape_node)
workflow.add_node("review", review_node)
workflow.add_edge("scrape", "review")
workflow.add_edge("review", END)
```

- [ ] **Step 3: Commit agent logic**

```bash
git add job-seek/src/agents/
git commit -m "feat: add langgraph orchestrator and reviewer sub-agent"
```

---

### Task 5: Interfaces (FastAPI & CLI)

**Files:**
- Create: `job-seek/src/api/main.py`
- Create: `job-seek/main.py` (CLI Entry)

- [ ] **Step 1: Implement FastAPI Routes**

```python
from fastapi import FastAPI
app = FastAPI()

@app.post("/jobs/search")
async def trigger_search():
    # Call LangGraph
    return {"status": "started"}
```

- [ ] **Step 2: Implement CLI with Typer**

```python
import typer
app = typer.Typer()

@app.command()
def search():
    # Run asyncio loop for LangGraph
    typer.echo("Searching for jobs...")

if __name__ == "__main__":
    app()
```

- [ ] **Step 3: Commit interfaces**

```bash
git add job-seek/src/api/main.py job-seek/main.py
git commit -m "feat: add fastapi and cli interfaces"
```

---

### Task 6: Emailer Integration (Resend)

**Files:**
- Create: `job-seek/src/utils/emailer.py`

- [ ] **Step 1: Implement Email formatting and dispatch**

```python
import resend

def send_job_email(jobs: list):
    html_content = "<h1>Top Job Matches</h1>"
    for job in jobs:
        html_content += f"<h3>{job['title']} at {job['company']}</h3><p>{job['desc']}</p><a href='{job['link']}'>Apply</a>"
    
    resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": "user@example.com",
        "subject": "Your Daily Job Matches",
        "html": html_content
    })
```

- [ ] **Step 2: Commit emailer**

```bash
git add job-seek/src/utils/emailer.py
git commit -m "feat: add emailer integration with Resend"
```
