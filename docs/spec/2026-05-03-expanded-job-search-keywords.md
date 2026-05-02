# Design Spec: Expanded Job Search Keywords (Aggressive Loop)

## 1. Goal
Support searching for multiple job titles simultaneously to increase job market coverage. Update the default profile to include more senior-level technology leadership roles.

## 2. Data Updates
### 2.1. `data/profile_index.json`
Update `target_job_titles` to include a broader range of roles as requested by the user:
- `Senior Manager` (clarified from "srt manager")
- `Director of Software Development`
- `IT Head`
- `Software Director`
- `CTO`, `VP of Engineering`, `Head of Engineering`, etc. (existing)

## 3. Implementation Strategy
### 3.1. Keyword Collection (`job-seek/main.py`)
Modify the `search` command logic:
- If `--keywords` is provided by the user, split it (e.g., by comma) into a list.
- If no keywords are provided, use the **entire list** of `target_job_titles` from `profile_index.json` instead of just the first one.

### 3.2. Parallel Scrape Execution
- **State Update:** Update `JobState` in `src/agents/graph.py` to change `keywords: str` to `keywords: List[str]`.
- **Scraper Orchestrator:** Update `src/scrapers/orchestrator.py`'s `run_parallel_scrapes` to accept `List[str]` for keywords.
- **Concurrency:** Use `asyncio.gather` to trigger all scrapers for **every** keyword in the list.
- **Deduplication:** The existing SQLite persistence in the `filter` node will naturally handle duplicates if the same job listing is found by multiple keywords.

## 4. Proposed Changes
### 4.1. `data/profile_index.json`
- Update the list of target titles.

### 4.2. `src/agents/graph.py`
- Update `JobState` type definition.
- Update `scrape_node` to handle the keyword list.

### 4.3. `src/scrapers/orchestrator.py`
- Update `run_parallel_scrapes` signature and implementation to loop through keywords or run them in a nested `gather`.

### 4.4. `job-seek/main.py`
- Update `search` command to extract and pass all titles.

## 5. Success Criteria
- Running `job-seek search` without arguments triggers searches for all titles in the profile.
- Results from all searches are aggregated, deduplicated, and reviewed.
- Performance remains acceptable through high levels of concurrency.
