# ----------------------------------------------------------------------
# SubscriberProfile loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseLoader
from ..models.subscriberprofile import SubscriberProfile
from noc.crm.models.subscriberprofile import SubscriberProfile as SubscriberProfileModel
from noc.wf.models.workflow import Workflow

DEFAULT_WORKFLOW_NAME = "Default Resource"


class SubscriberProfileLoader(BaseLoader):
    """
    Subscriber Profile loader
    """

    name = "subscriberprofile"
    model = SubscriberProfileModel
    data_model = SubscriberProfile

    def clean(self, row):
        d = super().clean(row)
        if "workflow" in d and d["workflow"]:
            d["workflow"] = Workflow.objects.get(name=d["workflow"])
        else:
            d["workflow"] = Workflow.objects.get(name=DEFAULT_WORKFLOW_NAME)
        return d
