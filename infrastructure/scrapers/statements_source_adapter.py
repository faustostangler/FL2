"""Statement source adapter for fetching financial reports."""

from __future__ import annotations

import random
import time
from typing import Any, Dict, List
from urllib.parse import quote_plus

# import pandas as pd
from bs4 import BeautifulSoup, Tag

from domain.dto import StatementRowsDTO, WorkerTaskDTO
from domain.dto.nsd_dto import NsdDTO
from domain.ports import LoggerPort, StatementSourcePort
from infrastructure.config import Config
from infrastructure.helpers.data_cleaner import DataCleaner
from infrastructure.helpers.fetch_utils import FetchUtils
from infrastructure.helpers.time_utils import TimeUtils
from infrastructure.utils.id_generator import IdGenerator


class RequestsStatementSourceAdapter(StatementSourcePort):
    """Fetch statement HTML using ``requests``."""

    def __init__(
        self, config: Config, logger: LoggerPort, data_cleaner: DataCleaner
    ) -> None:
        """Create the adapter with its configuration and logger."""
        self.config = config
        self.logger = logger
        self.data_cleaner = data_cleaner
        self.fetch_utils = FetchUtils(config, logger)
        self.time_utils = TimeUtils(self.config)
        self.session = self.fetch_utils.create_scraper()
        self.endpoint = f"{self.config.exchange.nsd_endpoint}"
        self.statements_config = self.config.statements
        self.id_generator = IdGenerator(config=config)

        # self.logger.log(f"Load Class {self.__class__.__name__}", level="info")

    def _parse_statement_page(
        self, soup: BeautifulSoup, group: str
    ) -> List[Dict[str, Any]]:
        """Return parsed rows from a statement ``soup``."""
        rows: List[Dict[str, Any]] = []

        # Default parsing for Capital Composition page
        if group == "Dados da Empresa":
            thousand = 1
            table = soup.find("div", id="UltimaTabela")
            if isinstance(table, Tag):
                text = table.get_text()
                if "Mil" in text:
                    thousand = 1000

            def value_from(elem_id: str) -> float:
                element = soup.find(id=elem_id)
                if element is None:
                    return 0.0
                value = self.data_cleaner.clean_number(element.get_text())
                result = thousand * value
                return result if result is not None else 0.0

            for item in self.statements_config.capital_items:
                rows.append(
                    {
                        "account": item["account"],
                        "description": item["description"],
                        "value": value_from(item["elem_id"]),
                    }
                )
            return rows

        # Default parsing for DFs pages
        thousand = 1
        title_element = soup.find(id="TituloTabelaSemBorda")
        if isinstance(title_element, Tag):
            title = title_element.get_text(strip=True)
            if "Mil" in title:
                thousand = 1000

        table = soup.find("table", id="ctl00_cphPopUp_tbDados")
        if not table:
            return rows

        if isinstance(table, Tag):
            table_rows = table.find_all("tr")
            for row in table_rows:
                cols = [c.get_text(strip=True) for c in row.find_all("td")]
                # ignora linhas cujo account não começa com dígito
                if len(cols) < 3:
                    continue
                if not cols[0] or not cols[0][0].isdigit():
                    continue
                account, account_description, account_value = cols[0], cols[1], cols[2]
                rows.append(
                    {
                        "account": account,
                        "description": account_description,
                        "value": (self.data_cleaner.clean_number(account_value) or 0.0)
                        * thousand,
                    }
                )

        return rows

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

    def fetch(self, task: WorkerTaskDTO) -> dict[str, Any]:
        """Fetch statement pages for the given NSD and return parsed rows."""
        # self.logger.log("Run  Method controller.run()._statement_service().statements_fetch_service.run().fetch_usecase.run().fetch_all().processor().source.fetch()", level="info")
        row = task.data

        url = self.endpoint.format(nsd=row.nsd)
        start = time.perf_counter()

        response, self.session = self.fetch_utils.fetch_with_retry(self.session, url)
        hash_value = self._extract_hash(response.text)

        statement_items = self.config.statements.statement_items
        statements_urls = self._build_urls(row, statement_items, hash_value)

        # Parse all statement pages
        statements_rows_dto: List[StatementRowsDTO] = []

        # for i, item in enumerate(statements_urls):
        for i in range(len(statements_urls)):
            item = statements_urls[i]

            quarter = row.quarter.strftime("%Y-%m-%d") if row.quarter else None
            for attempt in range(self.config.scraping.max_attempts):
                # self.time_utils.sleep_dynamic(multiplier=random.randint(5, 10))
                response, self.session = self.fetch_utils.fetch_with_retry(
                    self.session, item["url"]
                )
                soup = BeautifulSoup(response.text, "html.parser")

                blocked = (
                    "MensagemModal" in response.text
                    or "acesse este conteúdo pela página principal dos documentos"
                    in soup.get_text()
                )

                if not blocked:
                #     self.logger.log(
                #     f"{row.nsd} {row.company_name} {quarter} {row.version} - {i} {item['grupo']} {item['quadro']}",
                #     level="info",
                #     worker_id=task.worker_id,
                # )
                    break # sucess
                else:
                    self.session = self.fetch_utils.create_scraper()

                    # Tenta regenerar hash, embora neste caso hash_value_retry não seja usado
                    response_retry, self.session = self.fetch_utils.fetch_with_retry(self.session, url=url)
                    hash_value_retry = self._extract_hash(response_retry.text)
                    soup_retry = BeautifulSoup(response_retry.text, "html.parser")

                    # rebuild statements_urls
                    statements_urls = self._build_urls(row, statement_items, hash_value_retry)
                    item = statements_urls[i]

                    # self.logger.log(
                    #     f'{row.company_name} {quarter} {row.version} {row.nsd} - {i} {item["grupo"]} {item["quadro"]} retry_0{attempt+1}',
                    #     # f'{row.company_name} {quarter} {row.version} {row.nsd} - {i} {item["grupo"]} {item["quadro"]} \n{url}\n{item["url"]}\n\n',
                    #     level="warning",
                    #     worker_id=task.worker_id
                    # )
                    # self.time_utils.sleep_dynamic(multiplier=random.randint(5, 10) * attempt)
                    continue # new attempt
            else: # all attempts failed
                # self.logger.log(
                #     # f"{row.company_name} {quarter} {row.version} {row.nsd} - Aborted.",
                #     f"{row.company_name} {quarter} {row.version} {row.nsd} {url}... Aborted entire {quarter}.",
                #         level="warning",
                #         worker_id=task.worker_id,
                # )
                result: dict[str, Any] = {"nsd": row, "statements": []}
                self.time_utils.sleep_dynamic(multiplier=random.randint(5, 10))
                return result

            rows = self._parse_statement_page(soup, item["grupo"])
            parsed_rows = []

            for r in rows:
                dto = StatementRowsDTO(
                    nsd=row.nsd,
                    company_name=row.company_name,
                    quarter=quarter,
                    version=row.version,
                    grupo=item["grupo"],
                    quadro=item["quadro"],
                    account=r["account"],
                    description=r["description"],
                    value=r["value"],
                )
                parsed_rows.append(dto)

            statements_rows_dto.extend(parsed_rows)

        elapsed = time.perf_counter() - start
        quarter = row.quarter.strftime("%Y-%m-%d") if row.quarter else None
        # self.logger.log(
        #     f"{row.nsd} {row.company_name} {quarter} {row.version} in {elapsed:.2f}s",
        #     level="info",
        # )
        result = {"nsd": row, "statements": statements_rows_dto}

        # self.logger.log("End  Method controller.run()._statement_service().statements_fetch_service.run().fetch_usecase.run().fetch_all().processor().source.fetch()", level="info")

        return result
