"""Port definitions for company persistence repositories."""

from __future__ import annotations

from domain.dto.company_dto import CompanyDTO

from .base_repository_port import SqlAlchemyRepositoryBasePort


class SqlAlchemyCompanyRepositoryPort(SqlAlchemyRepositoryBasePort[CompanyDTO, str]):
    """Interface (port) for persistence operations related to Company entities.

    Acts as an abstraction for the application layer to interact with
    company-related data storage, decoupling it from the actual database implementation.
    """
