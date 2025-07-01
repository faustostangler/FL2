import pytest

from domain.dto.company_dto import CompanyDTO
from domain.dto.nsd_dto import NsdDTO


def test_company_dto_from_dict():
    raw = {"issuing_company": "XYZ", "company_name": "Xyz Corp"}
    dto = CompanyDTO.from_dict(raw)
    assert dto.issuing_company == "XYZ"
    assert dto.company_name == "Xyz Corp"


def test_nsd_dto_invalid_nsd():
    with pytest.raises(ValueError):
        NsdDTO.from_dict({"nsd": "not_a_number"})
