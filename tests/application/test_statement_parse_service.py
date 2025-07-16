from unittest.mock import MagicMock

from application.services.statement_parse_service import StatementParseService
from application.usecases.parse_and_classify_statements import (
    ParseAndClassifyStatementsUseCase,
)
from domain.dto import NsdDTO, StatementRowsDTO
from domain.ports import SqlAlchemyRawStatementRepository
from tests.conftest import DummyConfig, DummyLogger


def test_parse_statements_invokes_usecase_and_finalize(monkeypatch):
    dummy_config = DummyConfig()

    mock_usecase_cls = MagicMock(spec=ParseAndClassifyStatementsUseCase)
    mock_usecase_inst = MagicMock()
    mock_usecase_cls.return_value = mock_usecase_inst
    monkeypatch.setattr(
        "application.services.statement_parse_service.ParseAndClassifyStatementsUseCase",
        mock_usecase_cls,
    )

    repository = MagicMock(spec=SqlAlchemyRawStatementRepository)

    service = StatementParseService(
        logger=DummyLogger(),
        repository=repository,
        config=dummy_config,
        max_workers=2,
    )

    mock_usecase_cls.assert_called_once_with(
        logger=service.logger, repository=repository, config=dummy_config
    )

    parse_all = MagicMock()
    monkeypatch.setattr(service, "_parse_all", parse_all)

    fetched = [(MagicMock(spec=NsdDTO), [MagicMock(spec=StatementRowsDTO)])]

    service.parse_statements(fetched)

    parse_all.assert_called_once_with(fetched)
    mock_usecase_inst.finalize.assert_called_once()
