# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# vc.VCType tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.vc.models.vctype import VCType
from noc.core.comp import smart_text


@pytest.mark.parametrize(
    "data",
    [
        {"name": "Test 1", "min_labels": 1, "label1_min": 0, "label1_max": 15},
        {
            "name": "Test 2",
            "min_labels": 2,
            "label1_min": 0,
            "label1_max": 15,
            "label2_min": 0,
            "label2_max": 15,
        },
    ],
)
def test_insert(data):
    vc_type = VCType(**data)
    vc_type.save()
    for k in data:
        assert getattr(vc_type, k) == data[k]
    # Fetch record
    vc_type = VCType.objects.get(name=data["name"])
    assert vc_type.pk
    assert smart_text(vc_type)
    for k in data:
        assert getattr(vc_type, k) == data[k]
    # Delete record
    vc_type.delete()
