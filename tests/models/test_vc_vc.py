# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# vc.VC tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.vc.models.vctype import VCType
from noc.vc.models.vcdomain import VCDomain
from noc.vc.models.vc import VC
from noc.vc.models.error import InvalidLabelException
from noc.core.comp import smart_text


@pytest.mark.parametrize(
    "data",
    [
        {"vc_type": "802.1Q VLAN", "l1": 0, "$except": InvalidLabelException},
        {"vc_type": "802.1Q VLAN", "l1": 1},
        {"vc_type": "802.1Q VLAN", "l1": 100},
        {"vc_type": "802.1Q VLAN", "l1": 4095},
        {"vc_type": "802.1Q VLAN", "l1": 4096, "$except": InvalidLabelException},
    ],
)
def test_vc_labels(data):
    # Get type
    vc_type = VCType.objects.get(name=data["vc_type"])
    # Create temporary domain
    vc_domain = VCDomain(name="TEST DOMAIN", type=vc_type)
    vc_domain.save()
    vc = VC(vc_domain=vc_domain, name="TEST VC", l1=data.get("l1", 0), l2=data.get("l2", 0))
    if "$except" in data:
        with pytest.raises(data["$except"]):
            vc.save()
    else:
        vc.save()
        assert smart_text(vc)
        vc.delete()
    # Cleanup
    vc_domain.delete()
