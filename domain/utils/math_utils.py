"""Math helper functions for statement processing."""

from __future__ import annotations

from datetime import datetime


def parse_quarter(quarter: str | None) -> datetime | None:
    """Return ``datetime`` parsed from ISO date string."""
    if not quarter:
        return None
    try:
        return datetime.fromisoformat(quarter)
    except ValueError:
        return None


def quarter_index(dt: datetime) -> int:
    """Return quarter number (1-4) for ``dt``."""
    return (dt.month - 1) // 3 + 1
