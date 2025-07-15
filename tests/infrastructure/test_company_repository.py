from sqlalchemy import text

from domain.dto.company_data_dto import CompanyDataDTO
from infrastructure.models.base_model import Base
from infrastructure.repositories.company_repository import SqlAlchemyCompanyDataRepository
from tests.conftest import DummyConfig, DummyLogger


def test_save_all(SessionLocal, engine):
    repo = SqlAlchemyCompanyDataRepository(config=DummyConfig(), logger=DummyLogger())
    # use shared engine
    repo.engine = engine
    repo.Session = SessionLocal
    Base.metadata.create_all(engine)

    companies = [
        CompanyDataDTO.from_dict({"issuing_company": "AAA", "company_name": "Alpha"}),
        CompanyDataDTO.from_dict({"issuing_company": "BBB", "company_name": "Beta"}),
    ]
    repo.save_all(companies)

    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM tbl_company")).scalar()
    assert result == 2


def test_save_all_json_string(SessionLocal, engine):
    repo = SqlAlchemyCompanyDataRepository(config=DummyConfig(), logger=DummyLogger())
    repo.engine = engine
    repo.Session = SessionLocal
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    json_codes = '[{"code": "AAA", "isin": "123"}]'
    companies = [
        CompanyDataDTO.from_dict({"issuing_company": "AAA", "other_codes": json_codes})
    ]

    repo.save_all(companies)

    with engine.connect() as conn:
        saved = conn.execute(text("SELECT other_codes FROM tbl_company")).scalar()

    assert saved == json_codes


def test_save_all_upserts(SessionLocal, engine):
    repo = SqlAlchemyCompanyDataRepository(config=DummyConfig(), logger=DummyLogger())
    repo.engine = engine
    repo.Session = SessionLocal
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    first = [CompanyDataDTO.from_dict({"issuing_company": "AAA", "company_name": "Alpha"})]
    repo.save_all(first)

    second = [
        CompanyDataDTO.from_dict({"issuing_company": "AAA", "company_name": "Updated"})
    ]
    repo.save_all(second)

    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM tbl_company")).scalar()
        name = conn.execute(
            text("SELECT company_name FROM tbl_company WHERE cvm_code='AAA'")
        ).scalar()

    assert result == 1
    assert name == "Updated"
