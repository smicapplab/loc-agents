# Design Spec: Job-Filter Agent & Shared Core Refactor

## 1. Overview
An autonomous agent that reads job alert emails from your Gmail inbox (LinkedIn, Indeed, JobStreet), extracts job details, filters them by salary (>= 250k), scores them against your resume, and organizes them by moving them to the `#label/Jobs` label.

## 2. Refactored Structure (Shared Core)
To avoid code duplication, we will refactor the repository to use a shared `core` module.

```text
/Users/steve/Projects/Personal/loc-agents/
├── README.md
├── job-seek/                # Scraper Agent
│   ├── main.py
│   └── src/ (points to core)
├── job-filter/              # Email Agent (NEW)
│   ├── main.py
│   └── src/ (points to core)
└── src/                     # SHARED CORE
    ├── core/
    │   ├── db.py            # SQLite management
    │   ├── reviewer.py      # Gemini scoring
    │   ├── emailer.py       # Gmail SMTP sending
    │   └── profile/         # Resume management
    └── utils/
        └── pdf_processor.py
```

## 3. Job-Filter Features
- **Gmail API Integration:** Securely reads and manages labels in your inbox.
- **Time Filter:** Processes only emails received within the last **2 days**.
- **Source Filtering:** Specifically targets emails from `JobStreet`, `Indeed`, and `LinkedIn`.
- **Salary Floor:** Uses Gemini to identify published salaries and filters for **>= 250k**.
- **Label Management:**
    - Adds label: `Jobs`
    - Removes label: `Updates` (or Inbox)
- **Summary Notification:** Sends a curated summary email to `s.torrefranca@gmail.com`.

## 4. Technical Stack
- **API:** Google Gmail API (via `google-api-python-client`)
- **LLM:** Gemini 2.5 Flash (for extraction and scoring)
- **Shared Logic:** Reuse the existing `Reviewer` and `JobState` from the search project.

## 5. Sequence of Operations
1. **Gmail Search:** Query Gmail for messages from specific senders in the last 2 days.
2. **Parsing:** Extract the HTML/Text body of each email.
3. **Extraction (LLM):** Use Gemini to extract a list of jobs from the email content, specifically looking for salary data.
4. **Filtering:** Drop any jobs with published salaries < 250k.
5. **Scoring:** Score remaining jobs against the shared `profile.md`.
6. **Actions:**
    - Update SQLite to mark the email/job as processed.
    - Modify Gmail labels (Updates -> Jobs).
    - Dispatch summary email if high-score matches are found.

## 6. Implementation Plan (Summary)
1. **Phase 1: Shared Core:** Move `db.py`, `reviewer.py`, and `emailer.py` into a top-level `src/core`.
2. **Phase 2: Gmail Setup:** Guide the user through creating `credentials.json`.
3. **Phase 3: Filter Logic:** Implement the email parsing and salary extraction.
4. **Phase 4: CLI:** Create `job-filter/main.py`.
