# Job Filter Renaming Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rename `job_filter` to `job-filter` for consistency across the workspace and update all references.

**Architecture:** Rename directory and update imports and documentation.

**Tech Stack:** Python, Bash, Git

---

### Task 1: Rename Directory and Update Imports

**Files:**
- Rename: `job_filter/` -> `job-filter/`
- Modify: `job-filter/main.py`
- Modify: `tests/test_filter_logic.py`

- [ ] **Step 1: Rename the directory**

Run: `mv job_filter job-filter`

- [ ] **Step 2: Update imports in job-filter/main.py**

Change `from job_filter.logic import ...` to `from logic import ...`.

```python
<<<<
from job_filter.logic import extract_jobs_from_html, filter_by_salary, review_filtered_jobs
====
from logic import extract_jobs_from_html, filter_by_salary, review_filtered_jobs
>>>>
```

- [ ] **Step 3: Update imports and mocks in tests/test_filter_logic.py**

We need to make sure tests can still find the logic. Since `job-filter` is not a valid Python package name, we will need to adjust how we import it or how we run tests.
For now, let's update the imports to be relative or assume they are in the path.

Actually, a better way might be to keep the logic in a way that it can be imported. 
If we change `from job_filter.logic` to `from job_filter.logic` but the directory is `job-filter`, it won't work.

If we use `from .logic import ...` in `main.py` it might work if run as a package.

Let's try changing `tests/test_filter_logic.py` to import from `logic` directly and we will run pytest with `PYTHONPATH=job-filter`.

```python
<<<<
from job_filter.logic import extract_jobs_from_html, filter_by_salary
====
from logic import extract_jobs_from_html, filter_by_salary
>>>>
```
And update the patch:
```python
<<<<
@patch('job_filter.logic.genai.GenerativeModel')
====
@patch('logic.genai.GenerativeModel')
>>>>
```

- [ ] **Step 4: Verify tests pass**

Run: `PYTHONPATH=job-filter pytest tests/test_filter_logic.py`

- [ ] **Step 5: Commit**

```bash
git add job-filter tests/test_filter_logic.py
git commit -m "refactor: rename job_filter to job-filter and update imports"
```

### Task 2: Update Documentation and Gitignore

**Files:**
- Modify: `README.md`
- Modify: `.gitignore`

- [ ] **Step 1: Update .gitignore**

Check if there are any `job_filter` references. (Earlier check showed none, but let's be sure).
Also update project specific paths if any.

- [ ] **Step 2: Update README.md**

Add the Job Filter agent to the README if it's missing, and ensure all references use kebab-case.

- [ ] **Step 3: Verify all occurrences of job_filter are gone**

Run: `grep -r "job_filter" .` (should only show matches in docs/spec or plans)

- [ ] **Step 4: Commit**

```bash
git add README.md .gitignore
git commit -m "docs: update README and gitignore for job-filter renaming"
```
