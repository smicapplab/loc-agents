from .base import BaseScraper
from urllib.parse import quote
from typing import List, Dict
from crawl4ai import AsyncWebCrawler, JsonCssExtractionStrategy, CrawlerRunConfig
import json

class LinkedInScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.linkedin.com/jobs/search"
        
        # Schema for extracting job items from LinkedIn
        self.schema = {
            "name": "LinkedIn Jobs",
            "baseSelector": "div.base-card",
            "fields": [
                {"name": "title", "selector": "h3.base-search-card__title", "type": "text"},
                {"name": "company", "selector": "h4.base-search-card__subtitle", "type": "text"},
                {"name": "link", "selector": "a.base-card__full-link", "type": "attribute", "attribute": "href"},
                {"name": "posted_date", "selector": "time.job-search-card__listdate", "type": "attribute", "attribute": "datetime"}
            ]
        }
        self.extraction_strategy = JsonCssExtractionStrategy(self.schema)

    def build_search_url(self, keywords: str, location: str = "Philippines") -> str:
        query = quote(keywords)
        loc = quote(location)
        return f"{self.base_url}?keywords={query}&location={loc}&f_TPR=r604800"

    async def get_jobs(self, keywords: str, location: str = "Philippines") -> List[Dict]:
        url = self.build_search_url(keywords, location)
        
        run_config = CrawlerRunConfig(
            extraction_strategy=self.extraction_strategy,
            cache_mode=self.run_config.cache_mode
        )

        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            result = await crawler.arun(url=url, config=run_config)
            if result.success:
                try:
                    jobs = json.loads(result.extracted_content)
                    # Add IDs for deduplication
                    for job in jobs:
                        if job.get('link'):
                            job['id'] = job['link'].split('?')[0].split('/')[-1]
                    return jobs
                except:
                    return []
            return []

class SeekScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://ph.jobstreet.com"
        
        self.schema = {
            "name": "JobStreet Jobs",
            "baseSelector": "article",
            "fields": [
                {"name": "title", "selector": "a[data-automation='jobTitle']", "type": "text"},
                {"name": "company", "selector": "a[data-automation='jobCompany']", "type": "text"},
                {"name": "link", "selector": "a[data-automation='jobTitle']", "type": "attribute", "attribute": "href"},
                {"name": "posted_date", "selector": "span[data-automation='jobListingDate']", "type": "text"}
            ]
        }
        self.extraction_strategy = JsonCssExtractionStrategy(self.schema)

    def build_search_url(self, keywords: str) -> str:
        query = quote(keywords)
        # JobStreet uses /keywords-jobs in the URL
        # daterange=7 filters for the last 7 days
        return f"{self.base_url}/{query}-jobs?daterange=7"

    async def get_jobs(self, keywords: str) -> List[Dict]:
        url = self.build_search_url(keywords)
        
        run_config = CrawlerRunConfig(
            extraction_strategy=self.extraction_strategy,
            cache_mode=self.run_config.cache_mode
        )

        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            result = await crawler.arun(url=url, config=run_config)
            if result.success:
                try:
                    jobs = json.loads(result.extracted_content)
                    valid_jobs = []
                    for job in jobs:
                        if job.get('link') and job.get('title'):
                            if not job['link'].startswith('http'):
                                job['link'] = f"{self.base_url}{job['link']}"
                            job['id'] = job['link'].split('?')[0].split('/')[-1]
                            valid_jobs.append(job)
                    return valid_jobs
                except:
                    return []
            return []

class IndeedScraper(BaseScraper):
    # ... (Indeed implementation remains)
    def __init__(self):
        super().__init__()
        self.base_url = "https://ph.indeed.com/jobs"
        
        self.schema = {
            "name": "Indeed Jobs",
            "baseSelector": "div.job_seen_beacon",
            "fields": [
                {"name": "title", "selector": "h2.jobTitle span", "type": "text"},
                {"name": "company", "selector": "span[data-testid='company-name']", "type": "text"},
                {"name": "link", "selector": "a.jcs-JobTitle", "type": "attribute", "attribute": "href"},
                {"name": "posted_date", "selector": "span.date", "type": "text"}
            ]
        }
        self.extraction_strategy = JsonCssExtractionStrategy(self.schema)

    def build_search_url(self, keywords: str, location: str = "Philippines") -> str:
        query = quote(keywords)
        loc = quote(location)
        return f"{self.base_url}?q={query}&l={loc}&fromage=7"

    async def get_jobs(self, keywords: str, location: str = "Philippines") -> List[Dict]:
        url = self.build_search_url(keywords, location)
        
        run_config = CrawlerRunConfig(
            extraction_strategy=self.extraction_strategy,
            cache_mode=self.run_config.cache_mode
        )

        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            result = await crawler.arun(url=url, config=run_config)
            if result.success:
                try:
                    jobs = json.loads(result.extracted_content)
                    for job in jobs:
                        if job.get('link'):
                            if not job['link'].startswith('http'):
                                job['link'] = f"https://ph.indeed.com{job['link']}"
                            job['id'] = job['link'].split('jk=')[-1].split('&')[0]
                    return jobs
                except:
                    return []
            return []

class RemoteOKScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://remoteok.com"
        
        self.schema = {
            "name": "RemoteOK Jobs",
            "baseSelector": "tr.job",
            "fields": [
                {"name": "title", "selector": "h2[itemprop='title']", "type": "text"},
                {"name": "company", "selector": "h3[itemprop='name']", "type": "text"},
                {"name": "link", "selector": "a.preventLink", "type": "attribute", "attribute": "href"},
                {"name": "posted_date", "selector": "time", "type": "attribute", "attribute": "datetime"}
            ]
        }
        self.extraction_strategy = JsonCssExtractionStrategy(self.schema)

    def build_search_url(self, keywords: str) -> str:
        query = quote(keywords)
        return f"{self.base_url}/remote-{query}-jobs"

    async def get_jobs(self, keywords: str) -> List[Dict]:
        url = self.build_search_url(keywords)
        run_config = CrawlerRunConfig(
            extraction_strategy=self.extraction_strategy,
            cache_mode=self.run_config.cache_mode
        )
        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            result = await crawler.arun(url=url, config=run_config)
            if result.success:
                try:
                    jobs = json.loads(result.extracted_content)
                    for job in jobs:
                        if job.get('link'):
                            if not job['link'].startswith('http'):
                                job['link'] = f"{self.base_url}{job['link']}"
                            job['id'] = job['link'].split('/')[-1]
                    return jobs
                except:
                    return []
            return []

class WeWorkRemotelyScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://weworkremotely.com"
        
        self.schema = {
            "name": "WWR Jobs",
            "baseSelector": "li.feature",
            "fields": [
                {"name": "title", "selector": "span.title", "type": "text"},
                {"name": "company", "selector": "span.company", "type": "text"},
                {"name": "link", "selector": "a[href^='/remote-jobs/']", "type": "attribute", "attribute": "href"},
                {"name": "posted_date", "selector": "span.date", "type": "text"}
            ]
        }
        self.extraction_strategy = JsonCssExtractionStrategy(self.schema)

    def build_search_url(self, keywords: str) -> str:
        query = quote(keywords)
        return f"{self.base_url}/remote-jobs/search?term={query}"

    async def get_jobs(self, keywords: str) -> List[Dict]:
        url = self.build_search_url(keywords)
        run_config = CrawlerRunConfig(
            extraction_strategy=self.extraction_strategy,
            cache_mode=self.run_config.cache_mode
        )
        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            result = await crawler.arun(url=url, config=run_config)
            if result.success:
                try:
                    jobs = json.loads(result.extracted_content)
                    for job in jobs:
                        if job.get('link'):
                            if not job['link'].startswith('http'):
                                job['link'] = f"{self.base_url}{job['link']}"
                            job['id'] = job['link'].split('/')[-1]
                    return jobs
                except:
                    return []
            return []
