# Job-Filter Agent

An AI-powered agent that monitors your Gmail for job alerts, extracts listings, and scores them against your profile.

## Features
- **Gmail Integration:** Searches for emails from LinkedIn, Indeed, and JobStreet.
- **AI Extraction:** Uses OpenAI or Gemini to extract job details (title, salary, link) from email HTML.
- **Salary Filtering:** Automatically filters out jobs that don't meet your salary requirements.
- **Profile Scoring:** Uses the shared `Reviewer` agent to score matches against your resume.
- **Auto-Labeling:** Archives processed emails and tags matches with a "Jobs" label.

## Setup

1. **Dependencies:** Uses the same virtual environment and requirements as `job-seek`.
2. **Gmail API:** Requires `credentials.json` and `token.json` in the project root with `gmail.modify` scope.
3. **Configuration:** Uses the root `.env` for API keys and provider preferences.

## Usage

Run the agent from the project root using the provided script:
```bash
./scripts/job-filter.sh
```

## Architecture
- **Gmail API:** For email search and label management.
- **Shared Core:** Uses `src/core/reviewer.py` for scoring.
- **OpenAI/Gemini:** Flexible LLM support for extraction and evaluation.
