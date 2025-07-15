"""Base repository interface for persistence operations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, List, Set, TypeVar

T = TypeVar("T")   # DTO
K = TypeVar("K")   # Key type: str, int, etc.


class BaseRepositoryPort(ABC, Generic[T, K]):
    """Generic repository port for persistence operations."""

    @abstractmethod
    def save_all(self, items: List[T]) -> None:
        """Persist a batch of DTOs."""
        raise NotImplementedError

    @abstractmethod
    def get_all(self) -> List[T]:
        """Retrieve all items from the repository."""
        raise NotImplementedError

    @abstractmethod
    def has_item(self, identifier: K) -> bool:
        """Check if an item exists in the repository."""
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, id: K) -> T:
        """Retrieve an item by its identifier."""
        raise NotImplementedError

    @abstractmethod
    def get_all_primary_keys(self) -> Set[K]:
        """Retrieve the set of all primary keys already persisted."""
        raise NotImplementedError
