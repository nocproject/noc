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


class SubscriberProfileLoader(BaseLoader):
    """
    Subscriber Profile loader
    """

    name = "subscriberprofile"
    model = SubscriberProfile
    fields = ["id", "name", "description"]
