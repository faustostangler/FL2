from __future__ import annotations

from datetime import datetime
import time
from typing import List, Dict, Optional

import requests
from bs4 import BeautifulSoup

from infrastructure.config import Config
from infrastructure.logging import Logger
from infrastructure.helpers import FetchUtils
from infrastructure.helpers.data_cleaner import DataCleaner


class NsdScraper:
    """Scraper adapter responsible for fetching raw NSD documents."""

    def __init__(self, config: Config, logger: Logger, data_cleaner: DataCleaner):
        self.config = config
        self.logger = logger
        self.data_cleaner = data_cleaner
        self.fetch_utils = FetchUtils(config, logger)
        self.session = requests.Session()

        self.nsd_endpoint = self.config.b3.nsd_endpoint

        self.logger.log("Start NsdScraper", level="info")

    def fetch_all(self, start: int = 1, max_nsd: Optional[int] = None) -> List[Dict]:
        """Fetch and parse NSD pages.

        Args:
            start: First NSD number to fetch.
            limit: Optional amount of sequential NSDs to process. ``None``
                means fetch indefinitely until a page fails.

        Returns:
            List of dictionaries compatible with ``NSDDTO.from_dict``.
        """
        max_nsd = max_nsd or self.config.global_settings.threshold or 50
        self.logger.log("Fetch NSD list", level="info")

        nsd = start
        index = 0

        results: List[Dict] = []
        start_time = time.time()

        while True:
            progress = {"index": index, "size": max_nsd or 0, "start_time": start_time}
            url = self.nsd_endpoint.format(nsd=nsd)
            try:
                response = self.fetch_utils.fetch_with_retry(self.session, url)
            except Exception as e:
                self.logger.log(
                    f"Failed to fetch NSD {nsd}: {e}", level="warning",
                    progress=progress,
                )
                break

            parsed = self._parse_html(nsd, response.text)

            results.append(parsed) if parsed else None

            extra_info = [
                f"{parsed.get('nsd', nsd)}",  # usa o valor original do loop como fallback
                parsed["sent_date"].strftime("%Y-%m-%d %H:%M:%S") if parsed.get("sent_date") is not None else "",
                parsed.get("nsd_type", ""),
                parsed.get("company_name", ""),
                parsed["quarter"].strftime("%Y-%m") if parsed.get("quarter") is not None else "",
            ]

            extra_str = " ".join(str(e) for e in extra_info if e)

            self.logger.log(
                f"NSD", level="info",
                progress={**progress, "extra_info": extra_info},
            )

            if nsd >= max_nsd:
                break

            nsd += 1
            index += 1

        return results

    def _parse_html(self, nsd: int, html: str) -> Dict:
        """Parse NSD HTML into a dictionary."""

        soup = BeautifulSoup(html, "html.parser")

        def text_of(selector: str) -> Optional[str]:
            el = soup.select_one(selector)
            return el.get_text(strip=True) if el else None

        sent_date = text_of("#lblDataEnvio")
        if not sent_date:
            return {}

        # from DTO
        data: Dict[str, str | int | datetime | None] = {
            "nsd": nsd,
            "company_name": self.data_cleaner.clean_text(text_of("#lblNomeCompanhia")),

            # quarter e sent_date serão preenchidos depois
            "quarter": None,
            "version": None,
            "nsd_type": None,

            "dri": self.data_cleaner.clean_text(text_of("#lblNomeDRI")),
            "auditor": self.data_cleaner.clean_text(text_of("#lblAuditor")),
            "responsible_auditor": self.data_cleaner.clean_text(text_of("#lblResponsavelTecnico")),
            "protocol": text_of("#lblProtocolo"),
            "sent_date": None,
            "reason": self.data_cleaner.clean_text(text_of("#lblMotivoCancelamentoReapresentacao")),
        }

        quarter = text_of("#lblDataDocumento")
        if quarter and quarter.strip().isdigit() and len(quarter.strip()) == 4:
            quarter = f"31/12/{quarter.strip()}"
        data["quarter"] = self.data_cleaner.clean_date(quarter) if quarter else None

        nsd_type_version = text_of("#lblDescricaoCategoria")
        if nsd_type_version:
            parts = [p.strip() for p in nsd_type_version.split(" - ")]
            if len(parts) >= 2:
                data["version"] = self.data_cleaner.clean_text(parts[-1]) if parts[-1] else None
                data["nsd_type"] = self.data_cleaner.clean_text(parts[0]) if parts[0] else None

        data["sent_date"] = self.data_cleaner.clean_date(sent_date) if sent_date else None

        return data

