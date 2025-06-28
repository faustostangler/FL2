import types
from unittest.mock import MagicMock

from application.usecases.sync_companies import SyncCompaniesUseCase
# from domain.dto import CompanyDTO, SyncCompaniesResultDTO
from domain.dto.company_dto import CompanyDTO
from domain.ports import CompanyRepositoryPort, CompanySourcePort
from tests.conftest import DummyLogger


def test_execute_converts_and_saves():
    repo = MagicMock(spec=CompanyRepositoryPort)
    repo.get_all_primary_keys.return_value = {"SKIP"}

    raw = types.SimpleNamespace(
        cvm_code="001",
        company_name="Acme",
        ticker="ACM",
        ticker_codes=["ACM"],
        isin_codes=["BRACM"],
        trading_name="Acme",
        sector="Tech",
        subsector="Software",
        industry_segment="IT",
        listing="Novo Mercado",
        activity="Development",
        registrar="B3",
        cnpj="00.000.000/0001-91",
        website="example.com",
        company_type="SA",
        status="active",
        listing_date=None,
    )

    def fake_fetch_all(
        threshold=None, skip_codes=None, save_callback=None, max_workers=None
    ):
        assert skip_codes == {"SKIP"}
        if save_callback:
            save_callback([raw])
        return [raw]

    scraper = MagicMock(spec=CompanySourcePort)
    scraper.fetch_all.side_effect = fake_fetch_all
    scraper.metrics_collector = types.SimpleNamespace(network_bytes=100)

    usecase = SyncCompaniesUseCase(
        logger=DummyLogger(),
        repository=repo,
        scraper=scraper,
        max_workers=2,
    )

#     result = usecase.execute()
    usecase.execute()

    repo.get_all_primary_keys.assert_called_once()
    scraper.fetch_all.assert_called_once()
    repo.save_all.assert_called_once()
    saved = repo.save_all.call_args.args[0]
    assert isinstance(saved[0], CompanyDTO)
    assert saved[0].cvm_code == "001"

#     assert isinstance(result, SyncCompaniesResultDTO)
#     assert result.processed_count == 1
#     assert result.skipped_count == 1
#     assert result.bytes_downloaded == 100
