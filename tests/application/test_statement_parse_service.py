from unittest.mock import MagicMock

from application.services.statement_parse_service import StatementParseService
from application.usecases.parse_and_classify_statements import (
    ParseAndClassifyStatementsUseCase,
)
from application.usecases.persist_statements import PersistStatementsUseCase
from domain.ports import StatementRepositoryPort
from tests.conftest import DummyConfig, DummyLogger


def test_init_creates_persist_usecase(monkeypatch):
    repo = MagicMock(spec=StatementRepositoryPort)
    parse_usecase = MagicMock(spec=ParseAndClassifyStatementsUseCase)

    persist_cls = MagicMock(spec=PersistStatementsUseCase)
    persist_inst = MagicMock()
    persist_cls.return_value = persist_inst
    monkeypatch.setattr(
        "application.services.statement_parse_service.PersistStatementsUseCase",
        persist_cls,
    )

    service = StatementParseService(
        logger=DummyLogger(),
        parse_usecase=parse_usecase,
        statement_repo=repo,
        config=DummyConfig(),
    )

    persist_cls.assert_called_once_with(logger=service.logger, repository=repo)


def test_run_parses_and_persists(monkeypatch):
    repo = MagicMock(spec=StatementRepositoryPort)
    parse_usecase = MagicMock(spec=ParseAndClassifyStatementsUseCase)
    persist_cls = MagicMock(spec=PersistStatementsUseCase)
    persist_inst = MagicMock()
    persist_cls.return_value = persist_inst
    monkeypatch.setattr(
        "application.services.statement_parse_service.PersistStatementsUseCase",
        persist_cls,
    )

    service = StatementParseService(
        logger=DummyLogger(),
        parse_usecase=parse_usecase,
        statement_repo=repo,
        config=DummyConfig(),
    )

    parse_all = MagicMock(return_value=[[MagicMock()]])
    persist_all = MagicMock()
    monkeypatch.setattr(service, "_parse_all", parse_all)
    monkeypatch.setattr(service, "_persist_all", persist_all)

    fetched = [
        (
            MagicMock(),
            [MagicMock()],
        )
    ]

    service.run(fetched)

    parse_all.assert_called_once_with(fetched)
    persist_all.assert_called_once_with(parse_all.return_value)
