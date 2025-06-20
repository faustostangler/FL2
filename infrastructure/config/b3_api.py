from dataclasses import dataclass, field
from typing import Mapping

LANGUAGE = "pt-br"
ENDPOINTS = {
    "initial":   "https://sistemaswebb3-listados.b3.com.br/"
                    "listedCompaniesProxy/CompanyCall/GetInitialCompanies/",
    "detail":    "https://sistemaswebb3-listados.b3.com.br/"
                    "listedCompaniesProxy/CompanyCall/GetDetail/",
    "financial": "https://sistemaswebb3-listados.b3.com.br/"
                    "listedCompaniesProxy/CompanyCall/GetListedFinancial/"
}


@dataclass(frozen=True)
class B3ApiConfig:
    """
    B3 API endpoints configuration.
    Attributes:
        language: Language code for requests (fixed to "pt-br").
        endpoints: Mapping of logical names to B3 URLs.
    """
    language: str = field(default=LANGUAGE)
    endpoints: Mapping[str, str] = field(default_factory=lambda: ENDPOINTS)

def load_b3_api_config() -> B3ApiConfig:
    """
    Creates and returns an instance of B3ApiConfig with hard-coded language.
    """
    return B3ApiConfig(
        language  = LANGUAGE,
        endpoints = ENDPOINTS, 
    )
