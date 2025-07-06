from sqlalchemy import text

from domain.dto.statement_rows_dto import StatementRowsDTO
from infrastructure.models.base_model import Base
from infrastructure.repositories.statement_rows_repository import (
    SqlAlchemyStatementRowsRepository,
)
from tests.conftest import DummyConfig, DummyLogger


def test_save_all(SessionLocal, engine):
    repo = SqlAlchemyStatementRowsRepository(config=DummyConfig(), logger=DummyLogger())
    repo.engine = engine
    repo.Session = SessionLocal
    Base.metadata.create_all(engine)

    rows = [
        StatementRowsDTO(
            nsd=1,
            company_name="A",
            quarter="2024Q1",
            version="v1",
            grupo="G",
            quadro="Q",
            account="1",
            description="desc",
            value=10.0,
        )
    ]
    repo.save_all(rows)

    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM tbl_statements_raw")).scalar()
    assert result == 1
