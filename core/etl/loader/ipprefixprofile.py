# ----------------------------------------------------------------------
# PrefixProfile Loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseLoader
from ..models.ipprefixprofile import IPPrefixProfile
from noc.ip.models.prefixprofile import PrefixProfile
from noc.wf.models.workflow import Workflow

DEFAULT_WORKFLOW_NAME = "Default Resource"


class IPPrefixProfileLoader(BaseLoader):
    """
    Service Profile loader
    """

    name = "ipprefixprofile"
    model = PrefixProfile
    data_model = IPPrefixProfile

    def clean(self, row):
        d = super().clean(row)
        if "workflow" in d and d["workflow"]:
            d["workflow"] = Workflow.objects.get(name=d["workflow"])
        else:
            d["workflow"] = Workflow.get_default_workflow("ip.Prefix")
        return d
