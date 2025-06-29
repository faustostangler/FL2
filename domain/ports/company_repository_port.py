from __future__ import annotations
import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("domain > ports > company_repository_port")

from abc import ABC, abstractmethod
from typing import List, Set

from domain.dto.company_dto import CompanyDTO


class CompanyRepositoryPort(ABC):
    """Port for company persistence operations."""
    import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("company_repository_port.CompanyReposirotyPort(ABC)")

    @abstractmethod
    def save_all(self, items: List[CompanyDTO]) -> None:
        """Persist a batch of companies."""
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("class CompanyReposirotyPort(ABC).save_all()")
        raise NotImplementedError

    @abstractmethod
    def get_all_primary_keys(self) -> Set[str]:
        """Return all stored CVM codes."""
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("class CompanyReposirotyPort(ABC).get_all_primary_keys()")
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, id: str) -> CompanyDTO:
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("class CompanyReposirotyPort(ABC).get_by_id()")
        """Retrieve a company by its CVM code."""
        raise NotImplementedError
