import importlib

import pytest

from infrastructure.config import Config
from infrastructure.logging import Logger
from domain.dto.nsd_dto import NSDDTO


def test_sqlite_nsd_repository_save_and_get():
    repo_module = pytest.importorskip("infrastructure.repositories.nsd_repository")
    if not hasattr(repo_module, "SQLiteNSDRepository"):
        pytest.skip("SQLiteNSDRepository not implemented")

    SQLiteNSDRepository = getattr(repo_module, "SQLiteNSDRepository")

    config = Config()
    # force in-memory database
    object.__setattr__(config.database, "connection_string", "sqlite:///:memory:")
    logger = Logger(config)

    repo = SQLiteNSDRepository(config=config, logger=logger)

    sample = {
        "nsd": 1,
        "company_name": "Test",
        "quarter": "2024-Q1",
        "version": "1",
        "nsd_type": "DFP",
        "dri": "dri",
        "auditor": "aud",
        "responsible_auditor": "resp",
        "protocol": "prot",
        "sent_date": "2024-03-31",
        "reason": "ok",
    }

    dto = NSDDTO.from_dict(sample)
    repo.save_all([dto])
    results = repo.get_all()

    assert results == [dto]
