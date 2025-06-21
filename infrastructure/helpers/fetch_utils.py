from __future__ import annotations
import requests
import random
import time
from typing import Optional
from infrastructure.config import Config
from infrastructure.logging import Logger
from infrastructure.helpers.time_utils import TimeUtils


class FetchUtils:
    """
    Utility class for HTTP operations with retry and randomized headers.
    """

    def __init__(self, config: Config, logger: Logger):
        self.config = config
        self.logger = logger

    def header_random(self) -> dict:
        """
        Generate random HTTP headers based on scraping config.
        """
        try:
            return {
                "User-Agent": random.choice(self.config.scraping.user_agents),
                "Referer": random.choice(self.config.scraping.referers),
                "Accept-Language": random.choice(self.config.scraping.languages),
            }
        except Exception as e:
            self.logger.log(f"Header generation failed: {e}", level="warning")
            return {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                              "(KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36",
                "Referer": "https://www.google.com/",
                "Accept-Language": "en-US,en;q=0.9",
            }

    def test_internet(self, url: Optional[str] = None, timeout: Optional[int] = None) -> bool:
        """
        Checks if internet connection is active via HTTP GET request.
        """
        url = url or self.config.scraping.test_internet or "https://www.google.com"
        timeout = timeout or self.config.scraping.timeout or 5

        try:
            response = requests.get(url, timeout=timeout)
            return response.status_code == 200
        except Exception as e:
            self.logger.log(f"Internet test failed: {e}", level="debug")
            return False

    def fetch_with_retry(self, scraper, url: str, max_attempts: Optional[int] = None, timeout: Optional[int] = None):
        """
        Fetches a URL with retry and randomized headers.
        """
        max_attempts = max_attempts or self.config.scraping.max_attempts or 5
        timeout = timeout or self.config.scraping.timeout or 5

        for attempt in range(1, max_attempts + 1):
            try:
                response = scraper.get(url, headers=self.header_random())
                if response.status_code == 200:
                    return response
            except Exception as e:
                self.logger.log(f"Attempt {attempt} failed: {e}", level="warning")

            time_utils = TimeUtils(self.config)
            time_utils.sleep_dynamic()

        raise ConnectionError(f"Failed to fetch {url} after {max_attempts} attempts.")
