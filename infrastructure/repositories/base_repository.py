from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List

T = TypeVar("T")  # T pode ser CompanyDTO, StatementDTO, etc.

class BaseRepository(ABC, Generic[T]):
    """
    Contract - Interface genérica para repositórios de leitura/escrita.
    Pode ser especializada para qualquer tipo de DTO.
    """

    @abstractmethod
    def save_all(self, items: List[T]) -> None:
        """
        Saves in repository.
        """
        pass

    @abstractmethod
    def get_all(self) -> List[T]:
        """
        Get all items from repository.
        """
        pass

    @abstractmethod
    def has_item(self, identifier: str) -> bool:
        """
        Check if it is in repository.
        """
        pass

    @abstractmethod
    def get_by_id(self, id: str) -> T:
        """Recupera uma empresa a partir do ticker."""
        pass

