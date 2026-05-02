# Expanded Job Search Keywords Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Support searching for multiple job titles concurrently to increase job market coverage.

**Architecture:** Update the profile data to include new roles, refactor the LangGraph `JobState` to handle a list of keywords, and parallelize the scraping orchestrator to iterate over the keyword list while maintaining existing deduplication.

**Tech Stack:** Python, Typer, LangGraph, Crawl4AI, asyncio.

---

### Task 1: Update Profile Data

**Files:**
- Modify: `data/profile_index.json`

- [x] **Step 1: Update target_job_titles with new roles**

Modify `data/profile_index.json` to include the requested roles.

```json
{
  "target_job_titles": [
    "CTO",
    "VP of Engineering",
    "Head of Engineering",
    "Director of Software Development",
    "IT Head",
    "Senior Manager",
    "Software Director",
    "Chief Architect",
    "Head of Technology",
    "Solutions Architect (AI/Cloud/Fintech)",
    "Lead Consultant (AI/Fintech)"
  ]
}
```

- [x] **Step 2: Commit changes**

```bash
git add data/profile_index.json
git commit -m "data: expand target job titles in profile"
```

---

### Task 2: Refactor JobState and Scrape Node

**Files:**
- Modify: `src/agents/graph.py`

- [x] **Step 1: Update JobState type definition**

Change `keywords: str` to `keywords: List[str]`.

```python
from typing import TypedDict, List, Dict, Any

class JobState(TypedDict):
    keywords: List[str]  # Updated from str to List[str]
    location: str
    profile_md: str
    raw_jobs: List[Dict[str, Any]]
    new_jobs: List[Dict[str, Any]]
    scored_jobs: List[Dict[str, Any]]
```

- [x] **Step 2: Update scrape_node to log list of keywords**

```python
async def scrape_node(state: JobState) -> Dict[str, Any]:
    """Node: Scrapes job boards for the given keywords and location."""
    keywords_str = ", ".join(state['keywords'])
    print(f"Scraping jobs for keywords: [{keywords_str}] in {state['location']}...")
    jobs = await run_parallel_scrapes(state['keywords'], state['location'])
    return {"raw_jobs": jobs}
```

- [x] **Step 3: Commit changes**

```bash
git add src/agents/graph.py
git commit -m "feat: refactor JobState to support multiple keywords"
```

---

### Task 3: Update Scraper Orchestrator for Parallel Keyword Loops

**Files:**
- Modify: `src/scrapers/orchestrator.py`

- [x] **Step 1: Update run_parallel_scrapes signature and implementation**

Refactor to loop through all keywords and gather all results.

```python
import asyncio
from typing import List, Dict
from .board_scrapers import LinkedInScraper, SeekScraper, IndeedScraper, RemoteOKScraper, WeWorkRemotelyScraper

async def run_parallel_scrapes(keywords_list: List[str], location: str = "Philippines") -> List[Dict]:
    """
    Triggers all scrapers for every keyword in the list concurrently.
    """
    linkedin = LinkedInScraper()
    seek = SeekScraper()
    indeed = IndeedScraper()
    remoteok = RemoteOKScraper()
    wwr = WeWorkRemotelyScraper()

    async def scrape_for_keyword(kw):
        tasks = [
            linkedin.get_jobs(kw, location),
            seek.get_jobs(kw),
            indeed.get_jobs(kw, location),
            remoteok.get_jobs(kw),
            wwr.get_jobs(kw)
        ]
        return await asyncio.gather(*tasks)

    # Run searches for all keywords in parallel
    keyword_tasks = [scrape_for_keyword(kw) for kw in keywords_list]
    results_per_keyword = await asyncio.gather(*keyword_tasks)

    # Flatten results: keyword_tasks -> boards -> jobs
    all_jobs = []
    for keyword_results in results_per_keyword:
        for board_jobs in keyword_results:
            all_jobs.extend(board_jobs)

    print(f"Total jobs found across all keywords: {len(all_jobs)}")
    return all_jobs
```

- [x] **Step 2: Commit changes**

```bash
git add src/scrapers/orchestrator.py
git commit -m "feat: update orchestrator to handle keyword list in parallel"
```

---

### Task 4: Update CLI to pass keyword list

**Files:**
- Modify: `job-seek/main.py`

- [x] **Step 1: Update search command logic**

Extract all titles from profile if no keywords provided. Support comma-separated input for manual keywords.

```python
@app.command()
def search(
    keywords: str = typer.Option(None, help="Job keywords to search for (comma-separated). If not provided, will use all titles from profile_index.json"),
    location: str = typer.Option("Philippines", help="Location to search for jobs"),
    limit: int = typer.Option(5, help="Number of top matches to display")
):
    # ... existing profile loading code ...

    # 2. Determine Keywords List
    if keywords:
        # Support comma-separated keywords from CLI
        keywords_list = [k.strip() for k in keywords.split(",")]
    else:
        # Use all titles from profile
        keywords_list = profile_index.get("target_job_titles", ["Software Engineer"])
            
    typer.echo(f"Starting job hunt for keywords: {', '.join(keywords_list)} in {location}...")
    
    # 3. Initialize Graph
    graph = create_job_hunt_graph()
    
    # 4. Run Graph
    async def run_hunt():
        initial_state = {
            "keywords": keywords_list, # Now a list
            "location": location,
            "profile_md": profile_md,
            "raw_jobs": [],
            "new_jobs": [],
            "scored_jobs": []
        }
        
        result = await graph.ainvoke(initial_state)
        return result
    # ... rest of function ...
```

- [x] **Step 2: Verify with a dry run (limiting to 2 keywords for speed)**

Run: `python job-seek/main.py search --keywords "CTO, Senior Manager" --limit 1`
Expected: Logs showing "Scraping jobs for keywords: [CTO, Senior Manager]" and executing scrapers for both.

- [x] **Step 3: Commit changes**

```bash
git add job-seek/main.py
git commit -m "feat: update CLI to support multiple keywords and profile-wide search"
```
