from __future__ import annotations

import time

from domain.ports import LoggerPort, StatementSourcePort
from infrastructure.config import Config
from infrastructure.helpers.fetch_utils import FetchUtils


class RequestsStatementSourceAdapter(StatementSourcePort):
    """Fetch statement HTML using ``requests``."""

    def __init__(self, config: Config, logger: LoggerPort, endpoint: str):
        self.config = config
        self.logger = logger
        self._endpoint = endpoint
        self.fetch_utils = FetchUtils(config, logger)
        self.session = self.fetch_utils.create_scraper()
        self.logger.log("Start RequestsStatementSourceAdapter", level="info")

    @property
    def endpoint(self) -> str:  # pragma: no cover - simple accessor
        return self._endpoint

    def fetch(self, batch_id: str) -> str:
        url = self._endpoint.format(batch=batch_id)
        start = time.perf_counter()
        response = self.fetch_utils.fetch_with_retry(self.session, url)
        elapsed = time.perf_counter() - start
        self.logger.log(f"Fetched {batch_id} in {elapsed:.2f}s", level="info")
        return response.text
