# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# CHAlarmClass datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
from pymongo import ReadPreference
# NOC modules
from .base import BaseDataSource
from noc.fm.models.alarmclass import AlarmClass


class CHAlarmClassDataSource(BaseDataSource):
    name = "ch_alarmclass"

    def extract(self):
        for ac in AlarmClass.objects.filter(read_preference=ReadPreference.SECONDARY_PREFERRED).all().order_by("id"):
            yield (
                ac.bi_id,
                ac.id,
                ac.name
            )
