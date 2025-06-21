from __future__ import annotations

import time
from typing import List, Dict, Optional

import requests
from bs4 import BeautifulSoup

from infrastructure.config import Config
from infrastructure.logging import Logger
from infrastructure.helpers import FetchUtils


class NsdScraper:
    """Scraper adapter responsible for fetching raw NSD documents."""

    BASE_URL = "https://example.com/nsd/{nsd}"

    def __init__(self, config: Config, logger: Logger):
        self.config = config
        self.logger = logger
        self.fetch_utils = FetchUtils(config, logger)
        self.session = requests.Session()

        self.logger.log("Start NsdScraper", level="info")

    def fetch_all(self, start: int = 1, limit: Optional[int] = None) -> List[Dict]:
        """Fetch and parse NSD pages.

        Args:
            start: First NSD number to fetch.
            limit: Optional amount of sequential NSDs to process. ``None``
                means fetch indefinitely until a page fails.

        Returns:
            List of dictionaries compatible with ``NSDDTO.from_dict``.
        """

        self.logger.log("Fetch NSD list", level="info")

        results: List[Dict] = []
        start_time = time.time()

        nsd = start
        index = 0
        while True:
            if limit is not None and index >= limit:
                break

            url = self.BASE_URL.format(nsd=nsd)
            try:
                response = self.fetch_utils.fetch_with_retry(self.session, url)
            except Exception as e:
                self.logger.log(
                    f"Failed to fetch NSD {nsd}: {e}", level="warning",
                    progress={"index": index, "size": limit or 0, "start_time": start_time},
                )
                break

            parsed = self._parse_html(nsd, response.text)
            results.append(parsed)

            self.logger.log(
                f"Fetched NSD {nsd}", level="info",
                progress={"index": index, "size": limit or 0, "start_time": start_time},
            )

            nsd += 1
            index += 1

        return results

    def _parse_html(self, nsd: int, html: str) -> Dict:
        """Parse NSD HTML into a dictionary."""

        soup = BeautifulSoup(html, "html.parser")

        def get_value(label: str) -> Optional[str]:
            cell = soup.find("td", string=lambda x: x and label in x)
            if cell and cell.find_next("td"):
                return cell.find_next("td").get_text(strip=True)
            return None

        return {
            "nsd": nsd,
            "company_name": get_value("Companhia"),
            "quarter": get_value("Refer\u00eancia"),
            "version": get_value("Vers\u00e3o"),
            "nsd_type": get_value("Tipo"),
            "dri": get_value("Diretor"),
            "auditor": get_value("Auditor"),
            "responsible_auditor": get_value("Resp."),
            "protocol": get_value("Protocolo"),
            "sent_date": get_value("Envio"),
            "reason": get_value("Assunto"),
        }
