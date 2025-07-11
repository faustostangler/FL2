"""Port definitions for company persistence repositories."""

from __future__ import annotations

from domain.dto.company_dto import CompanyDTO

from .base_repository_port import BaseRepositoryPort


class CompanyRepositoryPort(BaseRepositoryPort[CompanyDTO]):
    """Port for company persistence operations."""

