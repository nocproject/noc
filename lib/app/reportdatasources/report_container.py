# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ReportObjectContainer datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
from collections import defaultdict
# Third-party modules
from pymongo import ReadPreference
# NOC modules
from .base import BaseReportDataSource
from noc.lib.nosql import get_db


class ReportContainer(BaseReportDataSource):
    """Report for MO Container"""
    UNKNOWN = {}

    @staticmethod
    def load(ids, attributes):
        match = {"data.management.managed_object": {"$exists": True}}
        if ids:
            match = {"data.management.managed_object": {"$in": ids}}
        value = get_db()["noc.objects"].with_options(read_preference=ReadPreference.SECONDARY_PREFERRED).aggregate([
            {"$match": match},
            {"$lookup": {"from": "noc.objects", "localField": "container", "foreignField": "_id", "as": "cont"}},
            {"$project": {"data": 1, "cont.data": 1}}
        ])

        r = defaultdict(dict)
        for v in value:
            if "asset" in v["data"]:
                r[v["data"]["management"]["managed_object"]].update(v["data"]["asset"])
            if v["cont"]:
                if "data" in v["cont"][0]:
                    r[v["data"]["management"]["managed_object"]].update(v["cont"][0]["data"].get("address", {}))
        # return dict((v["_id"][0], v["count"]) for v in value["result"] if v["_id"])
        return r
