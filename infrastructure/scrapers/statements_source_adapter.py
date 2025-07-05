"""Statement source adapter for fetching financial reports."""

from __future__ import annotations

import time
from typing import Any, Dict, List
from urllib.parse import quote_plus

# import pandas as pd
from bs4 import BeautifulSoup

from domain.dto.nsd_dto import NsdDTO
from domain.ports import LoggerPort, StatementSourcePort
from infrastructure.config import Config
from infrastructure.helpers.data_cleaner import DataCleaner
from infrastructure.helpers.fetch_utils import FetchUtils


class RequestsStatementSourceAdapter(StatementSourcePort):
    """Fetch statement HTML using ``requests``."""

    def __init__(self, config: Config, logger: LoggerPort, data_cleaner: DataCleaner):
        """Create the adapter with its configuration and logger."""
        self.config = config
        self.logger = logger
        self.data_cleaner = data_cleaner
        self.fetch_utils = FetchUtils(config, logger)
        self.session = self.fetch_utils.create_scraper()
        self.logger.log("Start RequestsStatementSourceAdapter", level="info")
        self.endpoint = f"{self.config.exchange.nsd_endpoint}"
        self.statements_config = self.config.statements
        self.parsed_rows: List[Dict[str, Any]] = []

    def _parse_statement_page(
        self, soup: BeautifulSoup, group: str
    ) -> List[Dict[str, Any]]:
        """Return parsed rows from a statement ``soup``."""
        results: List[Dict[str, Any]] = []

        if group == "Dados da Empresa":
            table = soup.find("div", id="UltimaTabela")
            table = table.find("table") if table else None
            thousand = 1000 if table and "Mil" in table.get_text() else 1

            def v(elem_id: str) -> float:
                el = soup.find(id=elem_id)
                if el is None:
                    return 0.0
                result = self.data_cleaner.clean_number(el.get_text())
                return result if result is not None else 0.0

            for item in self.statements_config.capital_items:
                results.append(
                    {
                        "account": item["account"],
                        "description": item["description"],
                        "value": v(item["elem_id"]),
                    }
                )
            return results

        # Default parsing for DFs pages
        title_el = soup.find(id="TituloTabelaSemBorda")
        thousand = 1000 if title_el and "Mil" in title_el.get_text() else 1
        table = soup.find("table", id="ctl00_cphPopUp_tbDados")
        if not table:
            return results

        for row in table.find_all("tr"):
            cols = [c.get_text(strip=True) for c in row.find_all("td")]
            if len(cols) < 3:
                continue
            account, desc, val = cols[0], cols[1], cols[2]
            results.append(
                {
                    "account": account,
                    "description": desc,
                    "value": (self.data_cleaner.clean_number(val) or 0.0) * thousand,
                }
            )

        return results

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
                base_url = (
                    self.statements_config.url_df
                    if item["grupo"].startswith("DFs")
                    else self.statements_config.url_capital
                )

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
        row_urls = self._build_urls(row, items, hash_value)

        # Parse all statement pages using the legacy logic
        self.parsed_rows = []
        for item in row_urls:
            response = self.fetch_utils.fetch_with_retry(self.session, item["url"])
            soup = BeautifulSoup(response.text, "html.parser")
            rows = self._parse_statement_page(soup, item["grupo"])
            for r in rows:
                r.update(
                    {
                        "grupo": item["grupo"],
                        "quadro": item["quadro"],
                        "company_name": row.company_name,
                        "nsd": row.nsd,
                        "quarter": row.quarter.strftime("%Y-%m-%d")
                        if row.quarter
                        else None,
                        "version": row.version,
                    }
                )
            self.parsed_rows.extend(rows)

        page_html = ""
        if row_urls:
            first_url = row_urls[0]["url"]
            stmt_response = self.fetch_utils.fetch_with_retry(self.session, first_url)
            page_html = stmt_response.text

        elapsed = time.perf_counter() - start
        self.logger.log(f"Fetched nsd {row.nsd} in {elapsed:.2f}s", level="info")
        return page_html
