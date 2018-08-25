# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ReportObjectIfacesTypeStat datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# Third-party modules
from pymongo import ReadPreference
# NOC modules
from .base import BaseReportColumn
from noc.lib.nosql import get_db


class ReportObjectIfacesTypeStat(BaseReportColumn):
    """Report for MO interfaces count"""
    name = "ifacestypestat"
    unknown_value = (0, )
    builtin_sorted = True

    def extract(self):
        i_type = "physical"
        match = {"type": i_type}
        if self.sync_ids:
            match = {"type": i_type,
                     "managed_object": {"$in": self.sync_ids}}
        value = get_db()["noc.interfaces"].with_options(
            read_preference=ReadPreference.SECONDARY_PREFERRED).aggregate(
            [
                {"$match": match},
                {"$group": {"_id": "$managed_object", "count": {"$sum": 1}}},
                {"$sort": {"_id": 1}}
            ])
        for v in value:
            if not v["_id"]:
                continue
            yield v["_id"], v["count"]
