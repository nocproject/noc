# ----------------------------------------------------------------------
# IP AddressProfile loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseLoader
from ..models.ipaddressprofile import IPAddressProfile
from noc.ip.models.addressprofile import AddressProfile
from noc.wf.models.workflow import Workflow

DEFAULT_WORKFLOW_NAME = "Default Resource"


class IPPrefixProfileLoader(BaseLoader):
    """
    Service Profile loader
    """

    name = "ipaddressprofile"
    model = AddressProfile
    data_model = IPAddressProfile

    def clean(self, row):
        d = super().clean(row)
        if "workflow" in d and d["workflow"]:
            d["workflow"] = Workflow.objects.get(name=d["workflow"])
        else:
            d["workflow"] = Workflow.get_default_workflow("ip.Address")
        return d
