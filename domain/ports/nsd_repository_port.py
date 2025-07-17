"""Port definitions for NSD persistence repositories."""

from __future__ import annotations

from domain.dto.nsd_dto import NsdDTO

from .base_repository_port import SqlAlchemyRepositoryBasePort


class NSDRepositoryPort(SqlAlchemyRepositoryBasePort[NsdDTO, str]):
    """Port for NSD persistence operations."""
