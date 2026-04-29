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
   source venv/bin/activate  # Or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   playwright install chromium
   ```

2. **Configure Environment:**
   Create a `.env` file in the `job-seek/` directory (see `.env.example`):
   ```text
   GOOGLE_API_KEY=your_gemini_api_key
   EMAIL_USER=your_gmail@gmail.com
   EMAIL_APP_PASSWORD=your_gmail_app_password
   EMAIL_TO=recipient@example.com
   ```

3. **Initialize Profile:**
   Place your resume at `data/resume.pdf` and run:
   ```bash
   PYTHONPATH=. python main.py sync
   ```

## Usage

### Run Job Hunt
Search for jobs and display top matches in the terminal:
```bash
PYTHONPATH=. python main.py search --limit 10
```

### Run Job Hunt with Email
Search and automatically email the top matches:
```bash
PYTHONPATH=. python main.py search --email
```

### Custom Keywords
```bash
PYTHONPATH=. python main.py search --keywords "Data Scientist" --email
```

## Architecture
- **LangGraph:** Orchestrates the scraping, filtering, and scoring workflow.
- **Crawl4AI:** Handles stealthy web scraping with CSS-based extraction.
- **Gemini 2.5 Flash:** Powers the resume structuring and job scoring.
- **SQLite:** Stores `data/jobs.db` for deduplication.
