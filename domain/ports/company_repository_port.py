"""Port definitions for company persistence repositories."""

from __future__ import annotations

from domain.dto.company_dto import CompanyDTO

from .base_repository_port import SqlAlchemyRepositoryBasePort


class SqlAlchemyCompanyRepositoryPort(SqlAlchemyRepositoryBasePort[CompanyDTO, str]):
    """Port for company persistence operations."""

