# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# CHServiceProfile datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
from pymongo import ReadPreference
# NOC modules
from .base import BaseDataSource
from noc.crm.models.subscriberprofile import SubscriberProfile


class CHProfileClassDataSource(BaseDataSource):
    name = "ch_subscriberprofile"

    def extract(self):
        for a in SubscriberProfile.objects.filter(
                read_preference=ReadPreference.SECONDARY_PREFERRED).all().order_by("id"):
            yield (
                a.bi_id,
                a.id,
                a.name,
                a.description,
                a.glyph
            )
