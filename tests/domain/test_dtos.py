from domain.dto.company_dto import CompanyDTO
from domain.dto.nsd_dto import NsdDTO


def test_company_dto_from_dict():
    raw = {"issuing_company": "XYZ", "company_name": "Xyz Corp"}
    dto = CompanyDTO.from_dict(raw)
    assert dto.issuing_company == "XYZ"
    assert dto.company_name == "Xyz Corp"


def test_nsd_dto_from_dict_casts_to_str():
    dto = NsdDTO.from_dict({"nsd": 123})
    assert dto.nsd == "123"
