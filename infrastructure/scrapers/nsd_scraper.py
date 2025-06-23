from __future__ import annotations

from datetime import datetime
import time
from typing import List, Dict, Optional, Callable

from bs4 import BeautifulSoup
import re

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
        self.session = self.fetch_utils.create_scraper()

        self.nsd_endpoint = self.config.b3.nsd_endpoint

        self.logger.log("Start NsdScraper", level="info")

    def fetch_all(
        self,
        start: int = 1,
        max_nsd: Optional[int] = None,
        skip_codes: Optional[set[int]] = None,
        save_callback: Optional[Callable[[list[dict]], None]] = None,
        threshold: Optional[int] = None,
    ) -> List[Dict]:
        """Fetch and parse NSD pages.

        Args:
            start: First NSD number to fetch.
            limit: Optional amount of sequential NSDs to process. ``None``
                means fetch indefinitely until a page fails.

        Returns:
            List of dictionaries compatible with ``NSDDTO.from_dict``.
        """
        skip_codes = skip_codes or set()
        start = max(start, max(skip_codes, default=0) + 1)
        max_nsd = max_nsd or self.find_last_existing_nsd(start=start) or 50
        threshold = threshold or self.config.global_settings.threshold or 50

        self.logger.log("Fetch NSD list", level="info")

        nsd = start
        index = 0

        buffer: list[dict] = []
        results: List[Dict] = []
        start_time = time.time()

        while nsd <= max_nsd:
            if nsd in skip_codes:
                nsd += 1
                index += 1
                continue

            total = max_nsd - start + 1
            completed = nsd - start + 1
            progress = {
                "index": (completed - 1),
                "size": (total) or (nsd - 1),
                "start_time": start_time,
            }

            url = self.nsd_endpoint.format(nsd=nsd)

            try:
                response = self.fetch_utils.fetch_with_retry(self.session, url)
                parsed = self._parse_html(nsd, response.text)
            except Exception as e:
                self.logger.log(
                    f"Failed to fetch NSD {nsd}: {e}",
                    level="warning",
                    progress=progress,
                )
                break

            if parsed:
                buffer.append(parsed)

            extra_info = [
                f"{parsed.get('nsd', nsd)}",  # usa o valor original do loop como fallback
                parsed["quarter"].strftime("%Y-%m-%d")
                if parsed.get("quarter") is not None
                else "",
                parsed.get("company_name", ""),
                parsed.get("nsd_type", ""),
                parsed["sent_date"].strftime("%Y-%m-%d %H:%M:%S")
                if parsed.get("sent_date") is not None
                else "",
            ]

            self.logger.log(
                "NSD",
                level="info",
                progress={**progress, "extra_info": extra_info},
            )

            # Condição de salvamento
            remaining = max_nsd - nsd
            if (remaining % threshold == 0) or (remaining == 0):
                if callable(save_callback) and buffer:
                    save_callback(buffer)
                    results.extend(buffer)
                    self.logger.log(f"Saved {len(buffer)} NSDs", level="info")
                    buffer.clear()

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
            "dri": None,
            "auditor": None,
            "responsible_auditor": self.data_cleaner.clean_text(
                text_of("#lblResponsavelTecnico")
            ),
            "protocol": text_of("#lblProtocolo"),
            "sent_date": None,
            "reason": self.data_cleaner.clean_text(
                text_of("#lblMotivoCancelamentoReapresentacao")
            ),
        }

        # Limpeza do padrão FCA
        dri = self.data_cleaner.clean_text(text_of("#lblNomeDRI")) or ""
        dri_pattern = r"\s+FCA(?:\s+V\d+)?\b"
        data["dri"] = re.sub(dri_pattern, "", dri)
        data["dri"] = re.sub(r"\s{2,}", " ", data["dri"]).strip()

        auditor = self.data_cleaner.clean_text(text_of("#lblAuditor")) or ""
        auditor_pattern = r"\s+FCA\s+\d{4}(?:\s+V\d+)?\b"
        data["auditor"] = re.sub(auditor_pattern, "", auditor)
        data["auditor"] = re.sub(r"\s{2,}", " ", data["auditor"]).strip()

        quarter = text_of("#lblDataDocumento")
        if quarter and quarter.strip().isdigit() and len(quarter.strip()) == 4:
            quarter = f"31/12/{quarter.strip()}"
        data["quarter"] = self.data_cleaner.clean_date(quarter) if quarter else None

        nsd_type_version = text_of("#lblDescricaoCategoria")
        if nsd_type_version:
            parts = [p.strip() for p in nsd_type_version.split(" - ")]
            if len(parts) >= 2:
                data["version"] = (
                    self.data_cleaner.clean_text(parts[-1]) if parts[-1] else None
                )
                data["nsd_type"] = (
                    self.data_cleaner.clean_text(parts[0]) if parts[0] else None
                )

        data["sent_date"] = (
            self.data_cleaner.clean_date(sent_date) if sent_date else None
        )

        return data

    def find_last_existing_nsd(self, start: int = 1, max_limit: int = 10**10) -> int:
        """
        Busca o maior NSD que realmente existe (tem conteúdo válido),
        usando busca exponencial seguida de busca binária.

        Args:
            start: valor inicial do NSD para tentar.
            max_limit: limite máximo de NSD a testar (fail-safe).

        Returns:
            Último NSD com conteúdo válido.
        """
        self.logger.log("Finding last existing NSD", level="info")
        nsd = start - 1
        last_valid = None

        max_linear_holes = self.config.global_settings.max_linear_holes or 2000
        hole_count = 0

        # Fase 1: busca linear até encontrar o primeiro válido
        while nsd <= max_limit and hole_count < max_linear_holes:
            # self.logger.log(f"Trying NSD {nsd} linear", level="info")
            parsed = self._try_nsd(nsd)
            if parsed:
                last_valid = nsd
                break
            nsd += 1
            hole_count += 1

        # Fase 2: Busca exponencial para achar um ponto inválido
        while nsd <= max_limit and hole_count < max_linear_holes:
            # self.logger.log(f"Trying NSD {nsd} exponential", level="info")
            parsed = self._try_nsd(nsd)
            if parsed:
                last_valid = nsd
                nsd *= 2
            else:
                break

        # Se nada válido foi encontrado, retorna o início
        if last_valid is None:
            return start

        # Fase 3: Busca binária entre último válido e primeiro inválido
        low = last_valid or 1
        high = nsd - 1

        while low < high:
            mid = (low + high + 1) // 2  # arredonda para cima para evitar loop infinito
            # self.logger.log(f"Trying NSD {mid} binary", level="info")
            parsed = self._try_nsd(mid)

            if parsed:
                low = mid  # é válido, sobe o piso
            else:
                high = mid - 1  # é inválido, desce o teto

        return low

    def _try_nsd(self, nsd: int) -> Optional[dict]:
        try:
            url = self.nsd_endpoint.format(nsd=nsd)
            response = self.fetch_utils.fetch_with_retry(self.session, url)
            parsed = self._parse_html(nsd, response.text)
            return parsed if parsed.get("sent_date") else None
        except Exception:
            return None
