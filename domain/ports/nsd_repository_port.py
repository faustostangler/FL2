"""Port definitions for NSD persistence repositories."""

from __future__ import annotations

from domain.dto.nsd_dto import NsdDTO

from .base_repository_port import BaseRepositoryPort


class NSDRepositoryPort(BaseRepositoryPort[NsdDTO]):
    """Port for NSD persistence operations."""
