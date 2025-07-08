from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from domain.dto.worker_class_dto import WorkerTaskDTO


class StatementSourcePort(ABC):
    """Port for fetching raw statement HTML."""

    @abstractmethod
    def fetch(self, task: WorkerTaskDTO) -> dict[str, Any]:
        """Return statement rows for the given NSD."""
        raise NotImplementedError
