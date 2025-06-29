import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("domain > dto > page_result_dto")
from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class PageResultDTO:
    """Container for paginated fetch results and metadata."""
    import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("page_result_dto class PageResultDTO")

    items: List[Dict]
    total_pages: int
    bytes_downloaded: int
