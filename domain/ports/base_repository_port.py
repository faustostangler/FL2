"""Base repository interface for persistence operations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, List, Sequence, Tuple, TypeVar, Union

T = TypeVar("T")   # DTO type
K = TypeVar("K")   # Key type (e.g., str, int)


class SqlAlchemyRepositoryBasePort(ABC, Generic[T, K]):
    """Generic interface (port) for basic repository operations.

    This abstract base class defines the standard CRUD-like operations
    expected from any persistence adapter, without assuming any specific
    database or storage technology.

    Type Args:
        T: DTO type being persisted.
        K: Identifier type for the primary key (e.g., str, int).
    """

    @abstractmethod
    def save_all(self, items: List[T]) -> None:
        """Persist a batch of domain DTOs.

        Args:
            items (List[T]): A list of DTOs to be saved to the repository.
        """
        raise NotImplementedError

    @abstractmethod
    def get_all(self) -> List[T]:
        """Retrieve all persisted items.

        Returns:
            List[T]: All items stored in the repository.
        """
        raise NotImplementedError

    @abstractmethod
    def has_item(self, identifier: K) -> bool:
        """Check whether an item with the given identifier exists.

        Args:
            identifier (K): The key to look up.

        Returns:
            bool: True if the item exists, False otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, identifier: K) -> T:
        """Retrieve a single item by its identifier.

        Args:
            id (K): The unique key for the item.

        Returns:
            T: The corresponding DTO.

        Raises:
            KeyError or ValueError: If the item is not found.
        """
        raise NotImplementedError

    @abstractmethod
    def get_all_primary_keys(self) -> List[K]:
        """Retrieve the set of all primary keys currently stored.

        Returns:
            Set[K]: A set of unique identifiers for all stored items.
        """
        raise NotImplementedError

    @abstractmethod
    def get_existing_by_columns(self, column_names: Union[str, List[str]]) -> List[Tuple]:
        """Retrieve the set of all primary keys currently stored by column.

        Returns:
            Set[K]: A set of unique identifiers for all stored items.
        """
        raise NotImplementedError

    @abstractmethod
    def _safe_cast(self, value: Any) -> Union[int, str]:
        raise NotImplementedError

    @abstractmethod
    def _sort_key(self, obj: Any, pk_columns: Sequence) -> tuple[Union[int, str], ...]:
        raise NotImplementedError

