import pytest

from domain.dto.company_dto import CompanyDTO
from domain.dto.nsd_dto import NSDDTO


def test_company_dto_from_dict():
    raw = {"ticker": "XYZ", "company_name": "Xyz Corp"}
    dto = CompanyDTO.from_dict(raw)
    assert dto.ticker == "XYZ"
    assert dto.company_name == "Xyz Corp"


def test_nsd_dto_invalid_nsd():
    with pytest.raises(ValueError):
        NSDDTO.from_dict({"nsd": "not_a_number"})
