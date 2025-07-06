import pytest

from domain.dto.company_dto import CompanyDTO
from domain.dto.nsd_dto import NsdDTO
from domain.dto.statement_rows_dto import StatementRowsDTO


def test_company_dto_from_dict():
    raw = {"issuing_company": "XYZ", "company_name": "Xyz Corp"}
    dto = CompanyDTO.from_dict(raw)
    assert dto.issuing_company == "XYZ"
    assert dto.company_name == "Xyz Corp"


def test_nsd_dto_invalid_nsd():
    with pytest.raises(ValueError):
        NsdDTO.from_dict({"nsd": "not_a_number"})


def test_statement_rows_dto_from_tuple():
    nsd = NsdDTO.from_dict({"nsd": 123})
    rows = [{"account": "1", "value": 10.0}]
    dto = StatementRowsDTO.from_tuple((nsd, rows))
    assert dto.nsd == nsd
    assert dto.rows == rows
