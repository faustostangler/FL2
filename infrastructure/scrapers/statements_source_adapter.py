"""Statement source adapter for fetching financial reports."""

from __future__ import annotations

import time
from urllib.parse import quote_plus

# import pandas as pd
from bs4 import BeautifulSoup

from domain.dto.nsd_dto import NsdDTO
from domain.ports import LoggerPort, StatementSourcePort
from infrastructure.config import Config
from infrastructure.helpers.fetch_utils import FetchUtils


class RequestsStatementSourceAdapter(StatementSourcePort):
    """Fetch statement HTML using ``requests``."""

    def __init__(self, config: Config, logger: LoggerPort):
        """Create the adapter with its configuration and logger."""
        self.config = config
        self.logger = logger
        self.fetch_utils = FetchUtils(config, logger)
        self.session = self.fetch_utils.create_scraper()
        self.logger.log("Start RequestsStatementSourceAdapter", level="info")
        self.endpoint = f"{self.config.exchange.nsd_endpoint}"
        self.statements_config = self.config.statements

    def _extract_hash(self, html: str) -> str:
        """Extract the hidden hash value from the HTML response."""
        soup = BeautifulSoup(html, "html.parser")
        element = soup.select_one("#hdnHash")
        if element is None:
            raise ValueError("Element with selector '#hdnHash' not found")
        value = element.get("value")
        if isinstance(value, list):
            value = value[0] if value else ""
        if not isinstance(value, str):
            raise ValueError("Expected a string value for 'value' attribute")
        return value

    def _build_urls(
        self, row: NsdDTO, items: list, hash_value: str
    ) -> list[dict[str, str]]:
        """Construct statement URLs using ``row`` data and the given hash."""
        nsd_type_map = self.statements_config.nsd_type_map

        doctype_name, doctype_code = nsd_type_map.get(
            row.nsd_type or "INFORMACOES TRIMESTRAIS",
            ("ITR", 3),
        )

        result: list[dict[str, str]] = []

        try:
            for item in items:
                base_url = self.statements_config.url_df if item["grupo"].startswith("DFs") else self.statements_config.url_capital

                params = {
                    "Grupo": item["grupo"],
                    "Quadro": item["quadro"],
                    "NomeTipoDocumento": doctype_name,
                    "Empresa": row.company_name,
                    "DataReferencia": row.quarter.strftime("%Y-%m-%d")
                    if row.quarter is not None
                    else "",
                    "Versao": row.version,
                    "CodTipoDocumento": str(doctype_code),
                    "NumeroSequencialDocumento": str(row.nsd),
                    "NumeroSequencialRegistroCvm": "",  # hardcoded
                    "CodigoTipoInstituicao": "1",  # hardcoded
                    "Hash": hash_value,
                }

                # Inclui os parâmetros extras (se presentes)
                for campo in ["informacao", "demonstracao", "periodo"]:
                    if item.get(campo) is not None:
                        params[campo.capitalize()] = str(item[campo])

                query = "&".join(f"{k}={quote_plus(str(v))}" for k, v in params.items())
                full_url = f"{base_url}?{query}"
                result.append(
                    {
                        "grupo": item["grupo"],
                        "quadro": item["quadro"],
                        "url": full_url,
                    }
                )
        except Exception as e:
            print(e)
        return result

    def fetch(self, row: NsdDTO) -> str:
        """Fetch HTML for the given NSD and return the first statement page."""
        url = self.endpoint.format(nsd=row.nsd)
        start = time.perf_counter()

        hash_response = self.fetch_utils.fetch_with_retry(self.session, url)
        hash_value = self._extract_hash(hash_response.text)

        items = self.config.statements.statement_items
        urls = self._build_urls(row, items, hash_value)

        page_html = ""
        if urls:
            first_url = urls[0]["url"]
            stmt_response = self.fetch_utils.fetch_with_retry(self.session, first_url)
            page_html = stmt_response.text

        elapsed = time.perf_counter() - start
        self.logger.log(f"Fetched nsd {row.nsd} in {elapsed:.2f}s", level="info")
        return page_html
