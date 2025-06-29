import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("infrastructure > base_repository")
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List

T = TypeVar("T")  # T pode ser CompanyDTO, StatementDTO, etc.

class BaseRepository(ABC, Generic[T]):
    """
    Contract - Interface genérica para repositórios de leitura/escrita.
    Pode ser especializada para qualquer tipo de DTO.
    """
    import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("base_repository.BaseRepository(ABC, Generic[T])")

    @abstractmethod
    def save_all(self, items: List[T]) -> None:
        """
        Saves in repository.
        """
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("BaseRepository(ABC, Generic[T]).save_all()")
        pass

    @abstractmethod
    def get_all(self) -> List[T]:
        """
        Get all items from repository.
        """
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("BaseRepository(ABC, Generic[T]).get_all()")
        pass

    @abstractmethod
    def has_item(self, identifier: str) -> bool:
        """
        Check if it is in repository.
        """
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("BaseRepository(ABC, Generic[T]).has_item()")
        pass

    @abstractmethod
    def get_by_id(self, id: str) -> T:
        """Recupera uma empresa a partir do ticker."""
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("BaseRepository(ABC, Generic[T]).get_by_id()")
        pass

