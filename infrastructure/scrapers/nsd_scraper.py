from __future__ import annotations

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

    BASE_URL = (
        "https://www.rad.cvm.gov.br/ENET/frmGerenciaPaginaFRE.aspx?"
        "NumeroSequencialDocumento={nsd}&CodigoTipoInstituicao=1"
    )

    def __init__(self, config: Config, logger: Logger, data_cleaner: DataCleaner):
        self.config = config
        self.logger = logger
        self.data_cleaner = data_cleaner
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
            if not parsed:
                break
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

        def text_of(selector: str) -> Optional[str]:
            el = soup.select_one(selector)
            return el.get_text(strip=True) if el else None

        data: Dict[str, Optional[str]] = {
            "nsd": nsd,
            "company_name": self.data_cleaner.clean_text(text_of("#lblNomeCompanhia")),
            "dri": self.data_cleaner.clean_text(text_of("#lblNomeDRI")),
            "auditor": self.data_cleaner.clean_text(text_of("#lblAuditor")),
            "responsible_auditor": self.data_cleaner.clean_text(text_of("#lblResponsavelTecnico")),
            "protocol": self.data_cleaner.clean_text(text_of("#lblProtocolo")),
            "reason": self.data_cleaner.clean_text(text_of("#lblMotivoCancelamentoReapresentacao")),
        }

        nsd_type_version = text_of("#lblDescricaoCategoria")
        quarter = text_of("#lblDataDocumento")
        sent_date = text_of("#lblDataEnvio")

        if nsd_type_version:
            parts = nsd_type_version.split()
            data["version"] = parts[-1]
            data["nsd_type"] = " ".join(parts[:-2])

        data["quarter"] = self.data_cleaner.clean_date(quarter)
        data["sent_date"] = self.data_cleaner.clean_date(sent_date)

        if data["sent_date"] is None:
            return {}

        return data
