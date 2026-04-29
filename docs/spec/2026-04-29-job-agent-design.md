# Design Spec: PH Job-Seek AI Agent

## 1. Overview
An autonomous AI agent designed to search, filter, and aggregate job listings from major job boards (LinkedIn, Seek, Indeed) specifically for the Philippines market (Onsite, Hybrid, Remote).

## 2. Goals
- **Automated Scraping:** Extract job data without being blocked by anti-bot measures, utilizing **parallel execution** for speed.
- **Resume-Centric Filtering:** Use a pre-processed resume profile to rank and filter jobs.
- **High Accuracy Review:** Use a **Reviewer Sub-Agent** to validate and cross-reference all collected postings against the user profile.
- **Persistence & Deduplication:** Use **SQLite** to store history and ensure the same job is never emailed twice.
- **Recency Focus:** Limit searches to jobs posted within the last **7 days**.
- **Unified Reporting:** Deliver a single, aggregated email with top matches.
- **Dual Interface:** Accessible via both a FastAPI web endpoint and a CLI tool.

## 3. Tech Stack
- **Language:** Python 3.11+
- **Agent Framework:** LangGraph (for stateful execution and sub-agent orchestration)
- **Scraper:** Crawl4AI (Open-source, LLM-friendly, stealth-capable)
- **LLM:** Gemini 2.0 Flash (via Google Generative AI API)
- **Database:** SQLite (for job history and deduplication)
- **Concurrency:** `asyncio` for parallel scraping
- **PDF Processing:** PyMuPDF (fitz)
- **API:** FastAPI
- **CLI:** Typer or argparse
- **Email:** Resend or standard SMTP

## 4. Architecture

### 4.1. Data Layer (`job-seek/data/`)
- `resume.pdf`: The source of truth for user profile.
- `profile.md`: LLM-generated professional persona.
- `profile_index.json`: Structured hard requirements (skills, location, seniority).
- `jobs.db`: SQLite database storing `job_id`, `title`, `company`, `link`, `date_emailed`, and `raw_desc`.

### 4.2. Functional Modules
1. **Resume Processor:** Converts PDF text into the Markdown/JSON profile.
2. **Search Orchestrator (The "Collector"):** A LangGraph state machine that runs board-specific scrapers in **parallel**.
3. **Reviewer Sub-Agent:** A specialized agent that takes the collection of "raw" jobs and performs a deep-dive comparison against the user's detailed resume.
4. **Deduplication Engine:** Checks SQLite before sending to ensure only new, high-score jobs are included.
5. **Emailer:** Formats and dispatches the final summary.

### 4.3. Interfaces
- **FastAPI:**
    - `POST /resume/sync`: Refresh profile from PDF.
    - `POST /jobs/search`: Run the job hunt.
- **CLI:**
    - `python main.py sync`: CLI version of resume sync.
    - `python main.py search`: CLI version of job search.

## 5. Sequence of Operations
1. **Pre-processing:** Extract text from `resume.pdf` -> Gemini structures it -> Write to `profile.md` & `profile_index.json`.
2. **Execution:**
   - Load `profile_index.json`.
   - **Parallel Scrape:** Trigger LinkedIn, Seek, and Indeed scrapers concurrently, filtered for `last 7 days`.
   - **Persistence Check:** Filter out any jobs already present in `jobs.db`.
   - **Review Phase:** The Reviewer Sub-Agent scores the *new* jobs (0-10).
   - **Aggregation:** Collect jobs with Score > 7.
   - **Delivery:** Update `jobs.db` and send Email.

## 6. Implementation Stages
1. **Base Setup:** Environment and folder structure.
2. **Resume Module:** PDF to MD/JSON conversion.
3. **Scraper Module:** Crawl4AI integration with board-specific logic.
4. **Agent Logic:** LangGraph workflow and Gemini filtering.
5. **Interface Layer:** FastAPI and CLI implementation.
6. **Delivery:** Email formatting and dispatch.
