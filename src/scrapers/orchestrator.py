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
