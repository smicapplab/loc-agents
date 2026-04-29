# Job-Filter Agent & Shared Core Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor the repository to use a shared core and implement a new `job-filter` agent that processes job alert emails from Gmail.

**Architecture:** Move shared utilities (DB, Reviewer, Emailer) to a top-level `src/core` folder. The `job-filter` agent will use the Gmail API to fetch messages, Gemini to extract job/salary data, and the shared Reviewer to score matches.

**Tech Stack:** Python, Gmail API, Gemini 2.5 Flash, SQLite, Typer.

---

### Task 1: Refactor to Shared Core

**Files:**
- Create: `src/core/db.py`, `src/core/reviewer.py`, `src/core/emailer.py`
- Create: `src/utils/pdf_processor.py`
- Modify: `job-seek/main.py`, `job-seek/src/agents/graph.py`, `job-seek/src/scrapers/orchestrator.py`

- [ ] **Step 1: Move existing utilities to top-level `src`**

```bash
mkdir -p src/core src/utils
cp job-seek/src/utils/db.py src/core/db.py
cp job-seek/src/agents/reviewer.py src/core/reviewer.py
cp job-seek/src/utils/emailer.py src/core/emailer.py
cp job-seek/src/utils/pdf_processor.py src/utils/pdf_processor.py
```

- [ ] **Step 2: Update `job-seek/src/agents/graph.py` imports**

```python
# From:
from src.scrapers.orchestrator import run_parallel_scrapes
from src.agents.reviewer import Reviewer
from src.utils.db import job_exists, init_db

# To:
from src.scrapers.orchestrator import run_parallel_scrapes
from src.core.reviewer import Reviewer
from src.core.db import job_exists, init_db
```

- [ ] **Step 3: Update `job-seek/main.py` imports**

```python
# From:
from src.utils.pdf_processor import extract_text_from_pdf, structure_resume
from src.agents.graph import create_job_hunt_graph
from src.utils.emailer import send_job_email
from src.utils.db import save_job, init_db

# To:
from src.utils.pdf_processor import extract_text_from_pdf, structure_resume
from src.agents.graph import create_job_hunt_graph
from src.core.emailer import send_job_email
from src.core.db import save_job, init_db
```

- [ ] **Step 4: Verify `job-seek` still works**

Run: `PYTHONPATH=. ./venv/bin/python job-seek/main.py search --limit 5`
Expected: Success logs and jobs found.

- [ ] **Step 5: Commit refactor**

```bash
git add src/ job-seek/
git commit -m "refactor: move shared logic to top-level src core"
```

---

### Task 2: Gmail API Integration

**Files:**
- Create: `src/core/gmail_api.py`

- [ ] **Step 1: Add Gmail API dependencies**

Update `job-seek/requirements.txt` (shared env for now):
```text
google-api-python-client
google-auth-httplib2
google-auth-oauthlib
```
Run: `./venv/bin/pip install -r job-seek/requirements.txt`

- [ ] **Step 2: Implement Gmail Client**

Create `src/core/gmail_api.py` with methods to:
1. Authenticate and save `token.json`.
2. Search messages (last 2 days, from LinkedIn/Indeed/JobStreet).
3. Get message body (HTML/Text).
4. Modify labels (Remove 'Updates', Add 'Jobs').

- [ ] **Step 3: Commit Gmail module**

```bash
git add src/core/gmail_api.py
git commit -m "feat: add gmail api integration for reading and labeling emails"
```

---

### Task 3: Job-Filter Logic & Salary Extraction

**Files:**
- Create: `job-filter/logic.py`

- [ ] **Step 1: Implement Job Extraction from Email Body**

Use Gemini to extract a list of jobs from the email HTML.
Prompt should look for: Title, Company, Link, Salary.

- [ ] **Step 2: Implement Salary Filter (>= 250k)**

```python
def filter_by_salary(job):
    salary = job.get('salary')
    if salary and salary >= 250000:
        return True
    return salary is None # Include if salary is not mentioned
```

- [ ] **Step 3: Implement Review & Score**

Re-use `Reviewer.review_job()` for the filtered jobs.

- [ ] **Step 4: Commit Filter Logic**

```bash
mkdir -p job-filter
git add job-filter/logic.py
git commit -m "feat: implement job extraction and salary filtering logic"
```

---

### Task 4: Job-Filter CLI

**Files:**
- Create: `job-filter/main.py`

- [ ] **Step 1: Implement CLI entry point**

Create `job-filter/main.py` with a `process` command that:
1. Fetches emails from the last 2 days.
2. Extracts jobs and filters by salary.
3. Scores them using the shared Reviewer.
4. Moves processed emails to `Jobs` label.
5. Sends summary email.

- [ ] **Step 2: Final Verification**

Run: `PYTHONPATH=. ./venv/bin/python job-filter/main.py process`
Expected: Emails processed and labels updated.

- [ ] **Step 3: Commit CLI**

```bash
git add job-filter/main.py
git commit -m "feat: add job-filter cli and complete implementation"
```
