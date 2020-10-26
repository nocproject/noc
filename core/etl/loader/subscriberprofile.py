# ----------------------------------------------------------------------
# SubscriberProfile loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseLoader
from ..models.subscriberprofile import SubscriberProfileModel
from noc.crm.models.subscriberprofile import SubscriberProfile
from noc.wf.models.workflow import Workflow

DEFAULT_WOKFLOW_NAME = "Default Resource"


class SubscriberProfileLoader(BaseLoader):
    """
    Subscriber Profile loader
    """

    name = "subscriberprofile"
    model = SubscriberProfile
    data_model = SubscriberProfileModel
    fields = ["id", "name", "description", "workflow"]

    def clean(self, row):
        d = super().clean(row)
        if "workflow" in d and d["workflow"]:
            d["workflow"] = Workflow.objects.get(name=d["workflow"])
        else:
            d["workflow"] = Workflow.objects.get(name=DEFAULT_WOKFLOW_NAME)
        return d
