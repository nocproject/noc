# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# CHVendor datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseDataSource
from noc.inv.models.vendor import Vendor


class CHVendorDataSource(BaseDataSource):
    name = "ch_vendor"

    def extract(self):
        for a in Vendor.objects.all().order_by("id"):
            yield (
                a.get_bi_id(),
                a.id,
                a.name
            )
