from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from typing import Optional
import os

class BaseScraper:
    def __init__(self):
        self.browser_config = BrowserConfig(
            headless=True,
            verbose=False,
            enable_stealth=True,
            extra_args=["--disable-blink-features=AutomationControlled"]
        )
        self.run_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            wait_until="domcontentloaded"
        )

    async def scrape_url(self, url: str) -> Optional[str]:
        """
        Scrapes a URL and returns its content in Markdown format.
        """
        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            result = await crawler.arun(
                url=url,
                config=self.run_config
            )
            if result.success:
                return result.markdown
            else:
                print(f"Failed to scrape {url}: {result.error_message}")
                return None
