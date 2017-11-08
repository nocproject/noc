# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# CHVendor datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import

from noc.inv.models.vendor import Vendor
from pymongo import ReadPreference

# NOC modules
from .base import BaseDataSource


class CHVendorDataSource(BaseDataSource):
    name = "ch_vendor"

    def extract(self):
        for a in Vendor.objects.filter(read_preference=ReadPreference.SECONDARY_PREFERRED).all().order_by("id"):
            yield (
                a.bi_id,
                a.id,
                a.name
            )
