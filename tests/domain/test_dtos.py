import pytest

from domain.dto.company_dto import CompanyDTO
from domain.dto.nsd_dto import NsdDTO
from domain.dto.raw_statement_dto import RawStatementDTO


def test_company_dto_from_dict():
    raw = {"issuing_company": "XYZ", "company_name": "Xyz Corp"}
    dto = CompanyDTO.from_dict(raw)
    assert dto.issuing_company == "XYZ"
    assert dto.company_name == "Xyz Corp"


def test_nsd_dto_invalid_nsd():
    with pytest.raises(ValueError):
        NsdDTO.from_dict({"nsd": "not_a_number"})


def test_raw_statement_dto_from_dict():
    raw = {
        "account": "00.01.01",
        "description": "A\u00e7\u00f5es ON Circulacao",
        "value": 0.0,
        "grupo": "Dados da Empresa",
        "quadro": "Composi\u00e7\u00e3o do Capital",
        "company_name": "Test Corp",
        "nsd": 123,
        "quarter": "2019-12-31",
        "version": "V1",
    }
    dto = RawStatementDTO.from_dict(raw)
    assert dto.account == "00.01.01"
    assert dto.company_name == "Test Corp"
    assert dto.nsd == 123
