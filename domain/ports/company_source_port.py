"""Port definitions for external company data sources."""

from __future__ import annotations

from domain.dto.raw_company_dto import CompanyRawDTO

from .base_source_port import BaseSourcePort


class CompanySourcePort(BaseSourcePort[CompanyRawDTO]):
    """Port for external company data providers."""

