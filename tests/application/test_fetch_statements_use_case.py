from unittest.mock import MagicMock

from application.usecases.fetch_statements import FetchStatementsUseCase
from domain.dto.nsd_dto import NsdDTO
from domain.ports import (
    StatementRowsRepositoryPort,
    StatementSourcePort,
)
from tests.conftest import DummyConfig, DummyLogger


def _make_nsd(nsd: int) -> NsdDTO:
    return NsdDTO(
        nsd=nsd,
        company_name=None,
        quarter=None,
        version=None,
        nsd_type=None,
        dri=None,
        auditor=None,
        responsible_auditor=None,
        protocol=None,
        sent_date=None,
        reason=None,
    )


def test_run_skips_existing(monkeypatch):
    source = MagicMock(spec=StatementSourcePort)
    rows_repo = MagicMock(spec=StatementRowsRepositoryPort)
    rows_repo.get_all_primary_keys.return_value = {"1"}

    usecase = FetchStatementsUseCase(
        logger=DummyLogger(),
        source=source,
        repository=rows_repo,
        config=DummyConfig(),
        max_workers=2,
    )

    mock_fetch_all = MagicMock(return_value=[("result", [])])
    monkeypatch.setattr(usecase, "fetch_all", mock_fetch_all)

    targets = [_make_nsd(1), _make_nsd(2)]
    result = usecase.run(targets, save_callback="cb", threshold=5)

    rows_repo.get_all_primary_keys.assert_called_once()
    mock_fetch_all.assert_called_once_with(
        targets=[targets[1]], save_callback="cb", threshold=5
    )
    assert result == mock_fetch_all.return_value
