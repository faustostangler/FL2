from unittest.mock import MagicMock

from application.services.statement_fetch_service import StatementFetchService
from application.usecases.fetch_statements import FetchStatementsUseCase
from domain.dto.nsd_dto import NsdDTO
from domain.ports import (
    CompanyRepositoryPort,
    NSDRepositoryPort,
    StatementRepositoryPort,
)
from tests.conftest import DummyConfig, DummyLogger


def test_run_calls_usecase(monkeypatch):
    dummy_config = DummyConfig()

    usecase = MagicMock(spec=FetchStatementsUseCase)

    company_repo = MagicMock(spec=CompanyRepositoryPort)
    nsd_repo = MagicMock(spec=NSDRepositoryPort)
    stmt_repo = MagicMock(spec=StatementRepositoryPort)

    service = StatementFetchService(
        logger=DummyLogger(),
        fetch_usecase=usecase,
        company_repo=company_repo,
        nsd_repo=nsd_repo,
        statement_repo=stmt_repo,
        config=dummy_config,
        max_workers=3,
    )

    targets = [MagicMock(spec=NsdDTO)]
    monkeypatch.setattr(service, "_build_targets", lambda: targets)

    result = service.run(save_callback="cb", threshold=5)

    usecase.run.assert_called_once_with(targets, save_callback="cb", threshold=5)
    assert result == usecase.run.return_value
