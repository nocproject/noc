# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# CHVersion datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseDataSource
from noc.inv.models.firmware import Firmware


class CHVersionDataSource(BaseDataSource):
    name = "ch_version"

    def extract(self):
        r = []
        for a in Firmware.objects.all().order_by("id"):
            r += [(
                a.get_bi_id(),
                a.id,
                a.name,
                a.profile.name,
                a.vendor.name
            )]
        return r
