from unittest.mock import MagicMock

from application.usecases.fetch_statements import FetchStatementsUseCase
from domain.dto.nsd_dto import NsdDTO
from domain.ports import (
# <<<<<<< ce8ela-codex/extend-fetchstatementsusecase-to-re-download-missing-nsds
# =======
#     StatementRepositoryPort,
# >>>>>>> 2025-07-03-Statements-Round-1
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
# <<<<<<< ce8ela-codex/extend-fetchstatementsusecase-to-re-download-missing-nsds
    rows_repo.get_all_primary_keys.return_value = {"1"}
# =======
#     stmt_repo = MagicMock(spec=StatementRepositoryPort)
#     stmt_repo.get_all_primary_keys.return_value = {"1"}
# >>>>>>> 2025-07-03-Statements-Round-1

    usecase = FetchStatementsUseCase(
        logger=DummyLogger(),
        source=source,
        repository=rows_repo,
# <<<<<<< ce8ela-codex/extend-fetchstatementsusecase-to-re-download-missing-nsds
# =======
#         statement_repository=stmt_repo,
# >>>>>>> 2025-07-03-Statements-Round-1
        config=DummyConfig(),
        max_workers=2,
    )

    mock_fetch_all = MagicMock(return_value=[("result", [])])
    monkeypatch.setattr(usecase, "fetch_all", mock_fetch_all)

    targets = [_make_nsd(1), _make_nsd(2)]
    result = usecase.run(targets, save_callback="cb", threshold=5)

# <<<<<<< ce8ela-codex/extend-fetchstatementsusecase-to-re-download-missing-nsds
    rows_repo.get_all_primary_keys.assert_called_once()
# =======
#     stmt_repo.get_all_primary_keys.assert_called_once()
# >>>>>>> 2025-07-03-Statements-Round-1
    mock_fetch_all.assert_called_once_with(
        targets=[targets[1]], save_callback="cb", threshold=5
    )
    assert result == mock_fetch_all.return_value
