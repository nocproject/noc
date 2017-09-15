# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# CHAlarmClass datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseDataSource
from noc.fm.models.alarmclass import AlarmClass


class CHAlarmClassDataSource(BaseDataSource):
    name = "ch_alarmclass"

    def extract(self):
        r = []
        for ac in AlarmClass.objects.all().order_by("id"):
            r += [(
                ac.get_bi_id(),
                ac.id,
                ac.name
            )]
        return r
