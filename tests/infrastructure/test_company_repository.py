from sqlalchemy import text

from domain.dto.company_dto import CompanyDTO
from infrastructure.models.company_model import Base
from infrastructure.repositories.company_repository import SQLiteCompanyRepository
from tests.conftest import DummyConfig, DummyLogger


def test_save_all(SessionLocal, engine):
    repo = SQLiteCompanyRepository(config=DummyConfig(), logger=DummyLogger())
    # use shared engine
    repo.engine = engine
    repo.Session = SessionLocal
    Base.metadata.create_all(engine)

    companies = [
        CompanyDTO.from_dict({"ticker": "AAA", "company_name": "Alpha"}),
        CompanyDTO.from_dict({"ticker": "BBB", "company_name": "Beta"}),
    ]
    repo.save_all(companies)

    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM tbl_company")).scalar()
    assert result == 2
