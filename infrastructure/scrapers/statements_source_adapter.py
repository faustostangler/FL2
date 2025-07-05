"""Statement source adapter for fetching financial reports."""

from __future__ import annotations

import time
from datetime import datetime
from urllib.parse import quote_plus, urlencode

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

        self.endpoints_config = {
            ("Dados da Empresa", "Composição do Capital"): {
                "Informacao": None,
                "Demonstracao": None,
                "Periodo": 0,
            },
            ("DFs Individuais", "Balanço Patrimonial Ativo"): {
                "Informacao": 1,
                "Demonstracao": 2,
                "Periodo": 0,
            },
            ("DFs Individuais", "Balanço Patrimonial Passivo"): {
                "Informacao": 1,
                "Demonstracao": 3,
                "Periodo": 0,
            },
            ("DFs Individuais", "Demonstração do Resultado"): {
                "Informacao": 1,
                "Demonstracao": 4,
                "Periodo": 0,
            },
            (
                "DFs Individuais",
                "Demonstração do Resultado Abrangente",
            ): {
                "Informacao": 1,
                "Demonstracao": 5,
                "Periodo": 0,
            },
            ("DFs Individuais", "Demonstração do Fluxo de Caixa"): {
                "Informacao": 1,
                "Demonstracao": 99,
                "Periodo": 0,
            },
            ("DFs Individuais", "Demonstração de Valor Adicionado"): {
                "Informacao": 1,
                "Demonstracao": 9,
                "Periodo": 0,
            },
            ("DFs Consolidadas", "Balanço Patrimonial Ativo"): {
                "Informacao": 2,
                "Demonstracao": 2,
                "Periodo": 0,
            },
            ("DFs Consolidadas", "Balanço Patrimonial Passivo"): {
                "Informacao": 2,
                "Demonstracao": 3,
                "Periodo": 0,
            },
            ("DFs Consolidadas", "Demonstração do Resultado"): {
                "Informacao": 2,
                "Demonstracao": 4,
                "Periodo": 0,
            },
            (
                "DFs Consolidadas",
                "Demonstração do Resultado Abrangente",
            ): {
                "Informacao": 2,
                "Demonstracao": 5,
                "Periodo": 0,
            },
            ("DFs Consolidadas", "Demonstração do Fluxo de Caixa"): {
                "Informacao": 2,
                "Demonstracao": 99,
                "Periodo": 0,
            },
            ("DFs Consolidadas", "Demonstração de Valor Adicionado"): {
                "Informacao": 2,
                "Demonstracao": 9,
                "Periodo": 0,
            },
        }

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

    def _build_urls(self, row: NsdDTO, items: list, hash_value: str) -> list[dict[str, str]]:
        """Construct statement URLs using ``row`` data and the given hash."""
        nsd_type_map = {
            "INFORMACOES TRIMESTRAIS": ("ITR", 3),
            "DEMONSTRACOES FINANCEIRAS PADRONIZADAS": ("DFP", 4),
        }

        doctype_name, doctype_code = nsd_type_map.get(
            row.nsd_type or "INFORMACOES TRIMESTRAIS",
            ("ITR", 3)
        )

        url_df = "https://www.rad.cvm.gov.br/ENET/frmDemonstracaoFinanceiraITR.aspx"
        url_capital = "https://www.rad.cvm.gov.br/ENET/frmDadosComposicaoCapitalITR.aspx"

        result: list[dict[str, str]] = []

        try:
            for item in items:
                base_url = url_df if item["grupo"].startswith("DFs") else url_capital

                params = {
                    "Grupo": item["grupo"],
                    "Quadro": item["quadro"],
                    "NomeTipoDocumento": doctype_name,
                    "Empresa": row.company_name,
                    "DataReferencia": row.quarter.strftime("%Y-%m-%d") if row.quarter is not None else "",
                    "Versao": row.version,
                    "CodTipoDocumento": str(doctype_code),
                    "NumeroSequencialDocumento": str(row.nsd),
                    "NumeroSequencialRegistroCvm": "", # hardcoded
                    "CodigoTipoInstituicao": "1", # hardcoded
                    "Hash": hash_value,
                }

                # Inclui os parâmetros extras (se presentes)
                for campo in ["informacao", "demonstracao", "periodo"]:
                    if item.get(campo) is not None:
                        params[campo.capitalize()] = str(item[campo])

                query = "&".join(f"{k}={quote_plus(str(v))}" for k, v in params.items())
                full_url = f"{base_url}?{query}"
                result.append({
                    "grupo": item["grupo"],
                    "quadro": item["quadro"],
                    "url": full_url,
                })
        except Exception as e:
            print(e)
        return result



    def fetch(self, row: NsdDTO) -> str:
        """Fetch HTML for the given NSD and return the first statement page."""
        def _parse_html_table(table_tag):
            rows = []
            for tr in table_tag.find_all("tr"):
                cols = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
                if cols:
                    rows.append(cols)
            return rows

        url = self.endpoint.format(nsd=row.nsd)
        start = time.perf_counter()

        hash_response = self.fetch_utils.fetch_with_retry(self.session, url)
        hash_value = self._extract_hash(hash_response.text)

        items = [
            {
                "grupo": "Dados da Empresa",
                "quadro": "Composição do Capital",
                "informacao": None,
                "demonstracao": None,
                "periodo": 0,
            },
            {
                "grupo": "DFs Individuais",
                "quadro": "Balanço Patrimonial Ativo",
                "informacao": 1,
                "demonstracao": 2,
                "periodo": 0,
            },
            {
                "grupo": "DFs Individuais",
                "quadro": "Balanço Patrimonial Passivo",
                "informacao": 1,
                "demonstracao": 3,
                "periodo": 0,
            },
            {
                "grupo": "DFs Individuais",
                "quadro": "Demonstração do Resultado",
                "informacao": 1,
                "demonstracao": 4,
                "periodo": 0,
            },
            {
                "grupo": "DFs Individuais",
                "quadro": "Demonstração do Resultado Abrangente",
                "informacao": 1,
                "demonstracao": 5,
                "periodo": 0,
            },
            {
                "grupo": "DFs Individuais",
                "quadro": "Demonstração do Fluxo de Caixa",
                "informacao": 1,
                "demonstracao": 99,
                "periodo": 0,
            },
            {
                "grupo": "DFs Individuais",
                "quadro": "Demonstração de Valor Adicionado",
                "informacao": 1,
                "demonstracao": 9,
                "periodo": 0,
            },
            {
                "grupo": "DFs Consolidadas",
                "quadro": "Balanço Patrimonial Ativo",
                "informacao": 2,
                "demonstracao": 2,
                "periodo": 0,
            },
            {
                "grupo": "DFs Consolidadas",
                "quadro": "Balanço Patrimonial Passivo",
                "informacao": 2,
                "demonstracao": 3,
                "periodo": 0,
            },
            {
                "grupo": "DFs Consolidadas",
                "quadro": "Demonstração do Resultado",
                "informacao": 2,
                "demonstracao": 4,
                "periodo": 0,
            },
            {
                "grupo": "DFs Consolidadas",
                "quadro": "Demonstração do Resultado Abrangente",
                "informacao": 2,
                "demonstracao": 5,
                "periodo": 0,
            },
            {
                "grupo": "DFs Consolidadas",
                "quadro": "Demonstração do Fluxo de Caixa",
                "informacao": 2,
                "demonstracao": 99,
                "periodo": 0,
            },
            {
                "grupo": "DFs Consolidadas",
                "quadro": "Demonstração de Valor Adicionado",
                "informacao": 2,
                "demonstracao": 9,
                "periodo": 0,
            },
        ]
        urls = self._build_urls(row, items, hash_value)


        try:
            data = {}
            for i, url in enumerate(urls):
                response = self.fetch_utils.fetch_with_retry(self.session, url["url"])
                soup = BeautifulSoup(response.text, "html.parser")

                if url["grupo"] == "Dados da Empresa":
                    table = soup.find("div", id=div_id).find("table")
                    rows = _parse_html_table(table)
                    data[url["grupo"]] = {}
                    data[url["grupo"]][url["quadro"]] = rows
        except Exception as e:
            self.logger(e)
        df = pd.read_html(StringIO(str(table)))[0]
        
        thousand = 1000 if "Mil" in str(df.iloc[0, 0]) else 1


        pass


        page_html = response.text
        if urls:
            first_url = urls[0]["url"]
            stmt_response = self.fetch_utils.fetch_with_retry(self.session, first_url)
            page_html = stmt_response.text

        elapsed = time.perf_counter() - start
        self.logger.log(f"Fetched {batch_id} in {elapsed:.2f}s", level="info")
        return page_html
