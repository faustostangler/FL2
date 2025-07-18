from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from domain.dto.worker_class_dto import WorkerTaskDTO


class RawStatementScraperPort(ABC):
    """Port for fetching raw statement HTML."""

    @abstractmethod
    def fetch(self, task: WorkerTaskDTO) -> dict[str, Any]:
        """Return statement rows for the given NSD wrapped in ``task``."""
        raise NotImplementedError
