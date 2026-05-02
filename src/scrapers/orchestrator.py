import asyncio
from typing import List, Dict
from .board_scrapers import LinkedInScraper, SeekScraper, IndeedScraper, RemoteOKScraper, WeWorkRemotelyScraper

async def run_parallel_scrapes(keywords_list: List[str], location: str = "Philippines") -> List[Dict]:
    """
    Triggers all scrapers for every keyword in the list concurrently with concurrency control.
    """
    linkedin = LinkedInScraper()
    seek = SeekScraper()
    indeed = IndeedScraper()
    remoteok = RemoteOKScraper()
    wwr = WeWorkRemotelyScraper()

    semaphore = asyncio.Semaphore(5)  # Max 5 concurrent scrapes

    async def safe_scrape(scraper_fn, *args):
        async with semaphore:
            try:
                return await scraper_fn(*args)
            except Exception as e:
                # Attempt to get a descriptive name for the scraper being run
                scraper_name = getattr(getattr(scraper_fn, "__self__", None), "__class__", scraper_fn).__name__
                print(f"Error during scraping with {scraper_name}: {e}")
                return []

    async def scrape_for_keyword(kw):
        tasks = [
            safe_scrape(linkedin.get_jobs, kw, location),
            safe_scrape(seek.get_jobs, kw),
            safe_scrape(indeed.get_jobs, kw, location),
            safe_scrape(remoteok.get_jobs, kw),
            safe_scrape(wwr.get_jobs, kw)
        ]
        results = await asyncio.gather(*tasks)
        return [job for board_jobs in results for job in board_jobs]

    # Run searches for all keywords in parallel
    keyword_tasks = [scrape_for_keyword(kw) for kw in keywords_list]
    results_per_keyword = await asyncio.gather(*keyword_tasks)

    # Flatten results
    all_jobs = [job for keyword_jobs in results_per_keyword for job in keyword_jobs]

    print(f"Total raw jobs found across all keywords: {len(all_jobs)}")

    # Simple deduplication using id or link
    unique_jobs = {}
    for job in all_jobs:
        job_id = job.get('id') or job.get('link')
        if job_id and job_id not in unique_jobs:
            unique_jobs[job_id] = job

    print(f"Total unique jobs: {len(unique_jobs)}")
    return list(unique_jobs.values())
