"""Base repository interface for persistence operations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, List, TypeVar

T = TypeVar("T")


class BaseRepositoryPort(ABC, Generic[T]):
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
    def has_item(self, identifier: str) -> bool:
        """Check if an item exists in the repository."""
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, id: str) -> T:
        """Retrieve an item by its identifier."""
        raise NotImplementedError

    # @abstractmethod
    # def get_all_primary_keys(self) -> Set[str]:
    #     """Return all stored CVM codes."""
    #     raise NotImplementedError
