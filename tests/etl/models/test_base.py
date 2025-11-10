# ----------------------------------------------------------------------
# BaseModel tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, Dict

# Third-party modules
import pytest

# NOC modules
from noc.core.etl.models.base import BaseModel
from noc.core.etl.models.typing import Reference


class Color(BaseModel):
    id: str
    name: str


class Pile(BaseModel):
    id: str
    parent: Reference["Pile"]
    color: Reference[Color]
    color2: Optional[Reference[Color]]


@pytest.mark.parametrize(
    ("model", "expected"),
    [(Color, {}), (Pile, {"parent": "pile", "color": "color", "color2": "color"})],
)
def test_mapped_fields(model: BaseModel, expected: Dict[str, str]):
    assert model.get_mapped_fields() == expected
