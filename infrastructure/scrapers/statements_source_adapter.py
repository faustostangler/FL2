"""Statement source adapter for fetching financial reports."""

from __future__ import annotations

import time
from datetime import datetime
from urllib.parse import quote_plus, urlencode

# import pandas as pd
from bs4 import BeautifulSoup

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
        return soup.select_one("#hdnHash")["value"]

    def _build_urls(self, row: dict, hash_value: str) -> list[dict]:
        """Construct statement URLs using ``row`` data and the given hash."""
        urls: list[dict] = []

        nsd_type_map = {
            "INFORMACOES TRIMESTRAIS": ("ITR", 3),
            "DEMONSTRACOES FINANCEIRAS PADRONIZADAS": ("DFP", 4),
        }

        nome_tipo_documento, cod_tipo_documento = nsd_type_map.get(
            row.get("nsd_type", "INFORMACOES TRIMESTRAIS"),
            ("ITR", 3),
        )

        nsd = row.get("nsd")
        cvm_code = row.get("cvm_code", "")
        empresa = row.get("company_name", "")
        quarter = row.get("quarter")
        if quarter:
            if hasattr(quarter, "strftime"):
                data_referencia = quarter.strftime("%Y-%m-%d")
            else:
                try:
                    data_referencia = datetime.fromisoformat(str(quarter)).strftime(
                        "%Y-%m-%d"
                    )
                except ValueError:
                    data_referencia = str(quarter)
        else:
            data_referencia = ""
        versao = row.get("version", "")
        nsd_type = row.get("nsd_type", "")

        for (grupo, quadro), params in self.endpoints_config.items():
            if grupo == "Dados da Empresa":
                base_url = (
                    "https://www.rad.cvm.gov.br/ENET/frmDadosComposicaoCapitalITR.aspx"
                )
            else:
                base_url = (
                    "https://www.rad.cvm.gov.br/ENET/frmDemonstracaoFinanceiraITR.aspx"
                )

            informacao = params["Informacao"]
            demonstracao = params["Demonstracao"]
            periodo = params["Periodo"]

            query = {
                "Grupo": grupo,
                "Quadro": quadro,
                "NomeTipoDocumento": nome_tipo_documento,
                "Empresa": empresa,
                "DataReferencia": data_referencia,
                "Versao": versao,
                "CodTipoDocumento": cod_tipo_documento,
                "NumeroSequencialDocumento": nsd,
                "NumeroSequencialRegistroCvm": cvm_code,
                "CodigoTipoInstituicao": 1,
                "Hash": hash_value,
                **({"Informacao": informacao} if informacao is not None else {}),
                **({"Demonstracao": demonstracao} if demonstracao is not None else {}),
                **({"Periodo": periodo} if periodo is not None else {}),
            }

            final_url = base_url + "?" + urlencode(query, quote_via=quote_plus)

            urls.append(
                {
                    "cvm_code": cvm_code,
                    "company_name": empresa,
                    "quarter": data_referencia,
                    "version": versao,
                    "nsd": nsd,
                    "nsd_type": nsd_type,
                    "grupo": grupo,
                    "quadro": quadro,
                    "nome_tipo_documento": nome_tipo_documento,
                    "cod_tipo_documento": cod_tipo_documento,
                    "url": final_url,
                }
            )

        return urls

    # @property
    # def endpoint(self) -> str:  # pragma: no cover - simple accessor
    #     return self._endpoint

    def fetch(self, batch_id: str) -> str:
        """Fetch HTML for the given NSD and return the first statement page."""
        url = self.endpoint.format(batch=batch_id)
        start = time.perf_counter()

        response = self.fetch_utils.fetch_with_retry(self.session, url)
        hash_value = self._extract_hash(response.text)

        dummy_row = {
            "nsd": batch_id,
            "cvm_code": "",
            "company_name": "",
            "quarter": "",
            "version": "",
            "nsd_type": "INFORMACOES TRIMESTRAIS",
        }

        urls = self._build_urls(dummy_row, hash_value)
        page_html = response.text
        if urls:
            first_url = urls[0]["url"]
            stmt_response = self.fetch_utils.fetch_with_retry(self.session, first_url)
            page_html = stmt_response.text

        elapsed = time.perf_counter() - start
        self.logger.log(f"Fetched {batch_id} in {elapsed:.2f}s", level="info")
        return page_html
