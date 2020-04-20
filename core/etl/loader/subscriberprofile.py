# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# SubscriberProfile loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import

# NOC modules
from .base import BaseLoader
from noc.crm.models.subscriberprofile import SubscriberProfile
from noc.wf.models.workflow import Workflow

DEFAULT_WOKFLOW_NAME = "Default Resource"


class SubscriberProfileLoader(BaseLoader):
    """
    Subscriber Profile loader
    """

    name = "subscriberprofile"
    model = SubscriberProfile
    fields = ["id", "name", "description", "workflow"]

    def clean(self, row):
        d = super(SubscriberProfileLoader, self).clean(row)
        if "workflow" in d:
            d["workflow"] = Workflow.objects.get(name=d["workflow"])
        else:
            d["workflow"] = Workflow.objects.get(name=DEFAULT_WOKFLOW_NAME)
        return d
