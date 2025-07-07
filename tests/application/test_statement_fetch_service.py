from unittest.mock import MagicMock

from application.services.statement_fetch_service import StatementFetchService
from application.usecases.fetch_statements import FetchStatementsUseCase
from domain.dto.nsd_dto import NsdDTO
from domain.ports import (
    CompanyRepositoryPort,
    NSDRepositoryPort,
    StatementRepositoryPort,
    StatementRowsRepositoryPort,
    StatementSourcePort,
)
from tests.conftest import DummyConfig, DummyLogger


def test_run_calls_usecase(monkeypatch):
    dummy_config = DummyConfig()

    mock_usecase_cls = MagicMock(spec=FetchStatementsUseCase)
    mock_usecase_inst = MagicMock()
    mock_usecase_cls.return_value = mock_usecase_inst
    monkeypatch.setattr(
        "application.services.statement_fetch_service.FetchStatementsUseCase",
        mock_usecase_cls,
    )

    company_repo = MagicMock(spec=CompanyRepositoryPort)
    nsd_repo = MagicMock(spec=NSDRepositoryPort)
    stmt_repo = MagicMock(spec=StatementRepositoryPort)
    rows_repo = MagicMock(spec=StatementRowsRepositoryPort)
    source = MagicMock(spec=StatementSourcePort)

    service = StatementFetchService(
        logger=DummyLogger(),
        source=source,
        statements_rows_repository=rows_repo,
        company_repo=company_repo,
        nsd_repo=nsd_repo,
        statement_repo=stmt_repo,
        config=dummy_config,
        max_workers=3,
    )

    mock_usecase_cls.assert_called_once_with(
        logger=service.logger,
        source=source,
        repository=rows_repo,
        statement_repository=stmt_repo,
        config=dummy_config,
        max_workers=3,
    )

    targets = [MagicMock(spec=NsdDTO)]
    monkeypatch.setattr(service, "_build_targets", lambda: targets)

    result = service.run(save_callback="cb", threshold=5)

    mock_usecase_inst.run.assert_called_once_with(
        targets, save_callback="cb", threshold=5
    )
    assert result == mock_usecase_inst.run.return_value
