import pytest

from domain.dto.company_data_dto import CompanyDataDTO
from domain.dto.nsd_dto import NsdDTO
from domain.dto.raw_statement_dto import RawStatementDTO


def test_company_dto_from_dict():
    raw = {"issuing_company": "XYZ", "company_name": "Xyz Corp"}
    dto = CompanyDataDTO.from_dict(raw)
    assert dto.issuing_company == "XYZ"
    assert dto.company_name == "Xyz Corp"


def test_nsd_dto_invalid_nsd():
    with pytest.raises(ValueError):
        NsdDTO.from_dict({"nsd": "not_a_number"})


def test_statement_rows_dto_from_dict():
    raw = {
        "account": "00.01.01",
        "description": "A\u00e7\u00f5es ON Circulacao",
        "value": 113548407.0,
        "grupo": "Dados da Empresa",
        "quadro": "Composi\u00e7\u00e3o do Capital",
        "company_name": "2W ECOBANK SA",
        "nsd": 102395,
        "quarter": "2020-12-31",
        "version": "V1",
    }
    dto = RawStatementDTO.from_dict(raw)
    assert dto.account == "00.01.01"
    assert dto.nsd == "102395"
