import asyncio
from typing import List, Dict
from .board_scrapers import LinkedInScraper, SeekScraper, IndeedScraper, RemoteOKScraper, WeWorkRemotelyScraper

async def run_parallel_scrapes(keywords: str, location: str = "Philippines") -> List[Dict]:
    """
    Triggers LinkedIn, Seek, Indeed, RemoteOK, and WWR scrapers concurrently.
    """
    linkedin = LinkedInScraper()
    seek = SeekScraper()
    indeed = IndeedScraper()
    remoteok = RemoteOKScraper()
    wwr = WeWorkRemotelyScraper()

    # Create tasks for all scrapers
    tasks = [
        linkedin.get_jobs(keywords, location),
        seek.get_jobs(keywords),
        indeed.get_jobs(keywords, location),
        remoteok.get_jobs(keywords),
        wwr.get_jobs(keywords)
    ]

    # Run concurrently and gather results
    results = await asyncio.gather(*tasks)

    source_names = ["LinkedIn", "Seek", "Indeed", "RemoteOK", "WWR"]
    for name, jobs in zip(source_names, results):
        print(f"[{name}] Found {len(jobs)} jobs")

    # Flatten the list of lists into a single list of job dicts
    flattened_jobs = [job for sublist in results for job in sublist]
    
    return flattened_jobs
