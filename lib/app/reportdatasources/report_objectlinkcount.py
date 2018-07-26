# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ReportObjectLinkCount datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# Third-party modules
from pymongo import ReadPreference
# NOC modules
from noc.lib.nosql import get_db
from .base import BaseReportStream


class ReportObjectLinkCount(BaseReportStream):
    """Report for MO link count"""
    name = "link_count"
    unknown_value = (0, )
    builtin_sorted = False

    def extract(self):
        value = get_db()["noc.links"].with_options(
            read_preference=ReadPreference.SECONDARY_PREFERRED).aggregate([
                {"$unwind": "$interfaces"},
                {"$lookup": {"from": "noc.interfaces",
                             "localField": "interfaces", "foreignField": "_id", "as": "int"}},
                {"$group": {"_id": "$int.managed_object", "count": {"$sum": 1}}}])
        for v in value:
            if not v["_id"]:
                continue
            yield v["_id"][0], v["count"]
