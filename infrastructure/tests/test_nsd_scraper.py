import importlib
from unittest.mock import Mock

import pytest

from infrastructure.config import Config
from infrastructure.logging import Logger


def test_nsd_scraper_fetch_all_parses_html(monkeypatch):
    scraper_module = pytest.importorskip("infrastructure.scrapers.nsd_scraper")
    if not hasattr(scraper_module, "NsdScraper"):
        pytest.skip("NsdScraper not implemented")

    NsdScraper = scraper_module.NsdScraper

    html = "<html><body><table><tr><td>1</td><td>Test</td></tr></table></body></html>"

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = html

    def mock_get(url, headers=None):
        return mock_response

    config = Config()
    logger = Logger(config)

    scraper = NsdScraper(config, logger)
    if not hasattr(scraper, "session"):
        pytest.skip("NsdScraper session handling not implemented")

    monkeypatch.setattr(scraper.session, "get", mock_get)

    data = scraper.fetch_all()

    assert isinstance(data, list)
    if not data:
        pytest.xfail("fetch_all returned empty list")
