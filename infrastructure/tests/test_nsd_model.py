import importlib

import pytest

from domain.dto.nsd_dto import NSDDTO


def test_nsd_model_roundtrip():
    nsd_model_module = pytest.importorskip("infrastructure.models.nsd_model")
    NSDModel = nsd_model_module.NSDModel

    sample = {
        "nsd": 123,
        "company_name": "Test Corp",
        "quarter": "2024-Q1",
        "version": "1",
        "nsd_type": "DFP",
        "dri": "dri",
        "auditor": "auditor",
        "responsible_auditor": "resp",
        "protocol": "prot",
        "sent_date": "2024-03-31",
        "reason": "reason",
    }

    dto = NSDDTO.from_dict(sample)
    model = NSDModel.from_dto(dto)
    result = model.to_dto()

    assert result == dto
