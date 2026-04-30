# PH Job-Seek AI Agent

An autonomous AI agent designed to search, filter, and aggregate job listings from major job boards (LinkedIn, Seek, Indeed, RemoteOK, and We Work Remotely) specifically for the Philippines and remote markets.

## Features
- **Parallel Scraping:** Fetches listings from 5 sources concurrently using Crawl4AI.
- **Intelligent Review:** Uses **Gemini 2.5 Flash** to score jobs (0-10) against your specific resume profile.
- **Persistence:** Uses SQLite to ensure you only see and receive emails for *new* jobs.
- **Gmail Integration:** Sends a formatted HTML email of the top-scoring matches.
- **Resume Sync:** One command to update your AI profile from a PDF resume.

## Setup

1. **Install Dependencies:**
   ```bash
   cd job-seek
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   playwright install chromium
   ```

2. **Configure Environment:**
   Create a `.env` file in the **root** directory (see `.env.example`).

3. **Usage via Scripts:**
   It is recommended to run the agent using the scripts in the project root:
   - Sync resume: `./scripts/job-seek.sh sync`
   - Search jobs: `./scripts/job-seek.sh search`

## Architecture
- **LangGraph:** Orchestrates the scraping, filtering, and scoring workflow.
- **Crawl4AI:** Handles stealthy web scraping with CSS-based extraction.
- **Gemini 2.5 Flash:** Powers the resume structuring and job scoring.
- **SQLite:** Stores `data/jobs.db` for deduplication.
