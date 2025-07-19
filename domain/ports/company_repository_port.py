"""Port definitions for company persistence repositories."""

from __future__ import annotations

from domain.dto.company_data_dto import CompanyDataDTO

from .base_repository_port import SqlAlchemyRepositoryBasePort


class SqlAlchemyCompanyDataRepositoryPort(
    SqlAlchemyRepositoryBasePort[CompanyDataDTO, int]
):
    """Interface (port) for persistence operations related to CompanyData
    entities.

    Acts as an abstraction for the application layer to interact with
    company-related data storage, decoupling it from the actual database
    implementation.
    """
