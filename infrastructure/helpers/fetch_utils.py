from __future__ import annotations

import random
import ssl
import time
from typing import Optional

import certifi
import requests
from requests.adapters import HTTPAdapter
from urllib3 import poolmanager

from domain.ports import LoggerPort
from infrastructure.config import Config
from infrastructure.helpers.time_utils import TimeUtils


class FetchUtils:
    """Utility class for HTTP operations with retry and randomized headers."""

    def __init__(self, config: Config, logger: LoggerPort) -> None:
        self.config = config
        self.logger = logger

        # self.logger.log(f"Load Class {self.__class__.__name__}", level="info")

    def header_random(self) -> dict:
        """Generate random HTTP headers based on scraping config."""
        try:
            return {
                "User-Agent": random.choice(self.config.scraping.user_agents),
                "Referer": random.choice(self.config.scraping.referers),
                "Accept-Language": random.choice(self.config.scraping.languages),
            }
        except Exception:
            # self.logger.log(f"Header generation failed: {e}", level="warning")
            return {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36",
                "Referer": "https://www.google.com/",
                "Accept-Language": "en-US,en;q=0.9",
            }

    def create_scraper(self, insecure: bool = False) -> requests.Session:
        """Return a configured requests session.

        Args:
            insecure: Whether to disable SSL verification.

        Returns:
            Configured ``requests.Session`` instance.
        """

        headers = self.header_random()

        session = requests.Session()
        session.headers.update(headers)

        if insecure:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            class InsecureAdapter(HTTPAdapter):
                def init_poolmanager(self, *args, **kwargs) -> None:  # type: ignore[override]
                    kwargs["ssl_context"] = context
                    self.poolmanager = poolmanager.PoolManager(*args, **kwargs)

            session.mount("https://", InsecureAdapter())
            session.verify = False
        else:
            session.verify = certifi.where()

        return session

    def test_internet(
        self, url: Optional[str] = None, timeout: Optional[int] = None
    ) -> bool:
        """Checks if internet connection is active via HTTP GET request."""
        url = url or self.config.scraping.test_internet or "https://www.google.com"
        timeout = timeout or self.config.scraping.timeout or 5

        try:
            response = requests.get(url, timeout=timeout)
            return response.status_code == 200
        except Exception as e:
            self.logger.log(f"Internet test failed: {e}", level="debug")
            return False

    def fetch_with_retry(
        self,
        scraper: Optional[requests.Session],
        url: str,
        timeout: Optional[int] = None,
        insecure: bool = False,
    ) -> tuple[requests.Response, requests.Session]:
        """Fetch a URL, recreating the scraper when blocked."""

        timeout = timeout or self.config.scraping.timeout or 5
        scraper = scraper or self.create_scraper(insecure=insecure)

        block_start = None
        attempt = 0

        while True:
            try:
                # Perform the request with the current session
                response = scraper.get(url, timeout=timeout)
                if response.status_code == 200:
                    # On success, log the total block time if any
                    if block_start:
                        _ = time.perf_counter() - block_start
                        # self.logger.log(
                        #     f"Dodging server block: {_:.2f}s",
                        #     level="warning",
                        # )
                    return response, scraper
            except Exception:  # noqa: BLE001
                # Ignore network errors and retry with a new scraper
                pass
                # self.logger.log(f"Attempt {attempt + 1} {url}", level="warning")

            # Record the start of blocking period on first failure
            if block_start is None:
                block_start = time.perf_counter()

            attempt += 1
            # Wait using dynamic sleep to avoid aggressive retries
            TimeUtils(self.config).sleep_dynamic()
            # Recreate the scraper session in case we were blocked
            scraper = self.create_scraper(insecure=insecure)
            # self.logger.log("Recreating scraper due to block", level="info")
