# ----------------------------------------------------------------------
# ServiceProfile loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseLoader
from ..models.serviceprofile import ServiceProfile
from noc.sa.models.serviceprofile import ServiceProfile as ServiceProfileModel
from noc.wf.models.workflow import Workflow

DEFAULT_WORKFLOW_NAME = "Service Default"


class ServiceProfileLoader(BaseLoader):
    """
    Service Profile loader
    """

    name = "serviceprofile"
    model = ServiceProfileModel
    data_model = ServiceProfile

    def clean(self, row):
        d = super().clean(row)
        if "workflow" in d and d["workflow"]:
            d["workflow"] = Workflow.objects.get(name=d["workflow"])
        else:
            d["workflow"] = Workflow.objects.get(name=DEFAULT_WORKFLOW_NAME)
        return d
