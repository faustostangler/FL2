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
    def get_by_id(self, id: str) -> T:
        """Retrieve an item by its identifier."""
        raise NotImplementedError
