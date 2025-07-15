from unittest.mock import MagicMock

# from application.services.company_services import CompanyService
from application.services.company_service import CompanyService
from application.usecases.sync_companies import SyncCompaniesUseCase
from domain.ports import CompanySourcePort, SqlAlchemyCompanyRepositoryPort
from tests.conftest import DummyConfig, DummyLogger


def test_sync_companies_calls_usecase(monkeypatch):
    dummy_config = DummyConfig()
    dummy_config.global_settings.max_workers = 3

    mock_usecase_cls = MagicMock(spec=SyncCompaniesUseCase)
    mock_usecase_inst = MagicMock()
    mock_usecase_cls.return_value = mock_usecase_inst
    monkeypatch.setattr(
        # "application.services.company_services.SyncCompaniesUseCase",
        "application.services.company_service.SyncCompaniesUseCase",
        mock_usecase_cls,
    )

    repo = MagicMock(spec=SqlAlchemyCompanyRepositoryPort)
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

    result = service.sync_companies()

    mock_usecase_inst.synchronize_companies.assert_called_once()
    assert result == mock_usecase_inst.synchronize_companies.return_value
