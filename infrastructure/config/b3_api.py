from dataclasses import dataclass, field
from typing import Mapping

LANGUAGE = "pt-br"
COMPANY_ENDPOINT = {
    "initial":   "https://sistemaswebb3-listados.b3.com.br/"
                    "listedCompaniesProxy/CompanyCall/GetInitialCompanies/",
    "detail":    "https://sistemaswebb3-listados.b3.com.br/"
                    "listedCompaniesProxy/CompanyCall/GetDetail/",
    "financial": "https://sistemaswebb3-listados.b3.com.br/"
                    "listedCompaniesProxy/CompanyCall/GetListedFinancial/"
}
NSD_ENDPOINT = (
    "https://www.rad.cvm.gov.br/ENET/frmGerenciaPaginaFRE.aspx?"
    "NumeroSequencialDocumento={nsd}&CodigoTipoInstituicao=1"
)


@dataclass(frozen=True)
class B3ApiConfig:
    """
    B3 API company_endpoint configuration.
    Attributes:
        language: Language code for requests (fixed to "pt-br").
        company_endpoint: Mapping of logical names to B3 URLs.
    """
    language: str = field(default=LANGUAGE)
    company_endpoint: Mapping[str, str] = field(default_factory=lambda: COMPANY_ENDPOINT)
    nsd_endpoint: str = field(default=NSD_ENDPOINT)

def load_b3_api_config() -> B3ApiConfig:
    """
    Creates and returns an instance of B3ApiConfig with hard-coded language.
    """

    return B3ApiConfig(
        language = LANGUAGE,
        company_endpoint = COMPANY_ENDPOINT,
        nsd_endpoint = NSD_ENDPOINT,
    )
