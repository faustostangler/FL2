from unittest.mock import MagicMock

from application.services.company_services import CompanyService
from application.usecases.sync_companies import SyncCompaniesUseCase
from domain.ports import CompanyRepositoryPort, CompanySourcePort
from tests.conftest import DummyConfig, DummyLogger


def test_run_calls_usecase_execute(monkeypatch):
    dummy_config = DummyConfig()
    dummy_config.global_settings.max_workers = 3

    mock_usecase_cls = MagicMock(spec=SyncCompaniesUseCase)
    mock_usecase_inst = MagicMock()
    mock_usecase_cls.return_value = mock_usecase_inst
    monkeypatch.setattr(
        "application.services.company_services.SyncCompaniesUseCase",
        mock_usecase_cls,
    )

    repo = MagicMock(spec=CompanyRepositoryPort)
    scraper = MagicMock(spec=CompanySourcePort)

    service = CompanyService(
        config=dummy_config,
        logger=DummyLogger(),
        repository=repo,
        scraper=scraper,
    )

    mock_usecase_cls.assert_called_once_with(
        logger=service.logger,
        repository=repo,
        scraper=scraper,
        max_workers=3,
    )

    service.run()

    mock_usecase_inst.execute.assert_called_once()
