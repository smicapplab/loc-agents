from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from src.scrapers.orchestrator import run_parallel_scrapes
from src.agents.reviewer import Reviewer
from src.utils.db import job_exists, init_db
import os

class JobState(TypedDict):
    keywords: str
    location: str
    profile_md: str
    raw_jobs: List[Dict[str, Any]]
    new_jobs: List[Dict[str, Any]]
    scored_jobs: List[Dict[str, Any]]

async def scrape_node(state: JobState) -> Dict[str, Any]:
    """Node: Scrapes job boards for the given keywords and location."""
    print(f"Scraping jobs for '{state['keywords']}' in {state['location']}...")
    jobs = await run_parallel_scrapes(state['keywords'], state['location'])
    return {"raw_jobs": jobs}

async def filter_node(state: JobState) -> Dict[str, Any]:
    """Node: Filters out jobs that already exist in the database."""
    await init_db()
    new_jobs = []
    for job in state['raw_jobs']:
        if not await job_exists(job['id']):
            new_jobs.append(job)
    
    print(f"Found {len(state['raw_jobs'])} raw jobs, {len(new_jobs)} are new.")
    return {"new_jobs": new_jobs}

async def review_node(state: JobState) -> Dict[str, Any]:
    """Node: Scores each new job using the Reviewer agent."""
    reviewer = Reviewer()
    scored_jobs = []
    
    # We only review the first 20 new jobs to save tokens/time in this version
    # Real-world might process all or a larger batch
    jobs_to_review = state['new_jobs'][:20]
    
    print(f"Reviewing {len(jobs_to_review)} jobs...")
    for job in jobs_to_review:
        scored_job = await reviewer.review_job(job, state['profile_md'])
        if scored_job['score'] >= 7:
            scored_jobs.append(scored_job)
            
    # Sort by score descending
    scored_jobs.sort(key=lambda x: x['score'], reverse=True)
    return {"scored_jobs": scored_jobs}

def create_job_hunt_graph():
    """Builds and returns the LangGraph workflow."""
    workflow = StateGraph(JobState)

    # Add nodes
    workflow.add_node("scrape", scrape_node)
    workflow.add_node("filter", filter_node)
    workflow.add_node("review", review_node)

    # Define edges
    workflow.set_entry_point("scrape")
    workflow.add_edge("scrape", "filter")
    workflow.add_edge("filter", "review")
    workflow.add_edge("review", END)

    return workflow.compile()
