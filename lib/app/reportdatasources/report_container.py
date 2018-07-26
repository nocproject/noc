# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ReportObjectContainer datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# Third-party modules
from pymongo import ReadPreference
# NOC modules
from .base import BaseReportStream
from noc.lib.nosql import get_db


class ReportContainer(BaseReportStream):
    """Report for MO Container"""
    # @container address by container
    name = "containeraddress"
    unknown_value = ({}, )
    builtin_sorted = True

    def extract(self):
        match = {"data.management.managed_object": {"$exists": True}}
        if self.sync_ids:
            match = {"data.management.managed_object": {"$in": self.sync_ids}}
        value = get_db()["noc.objects"].with_options(read_preference=ReadPreference.SECONDARY_PREFERRED).aggregate([
            {"$match": match},
            {"$sort": {"data.management.managed_object": 1}},
            {"$lookup": {"from": "noc.objects", "localField": "container", "foreignField": "_id", "as": "cont"}},
            {"$project": {"data": 1, "cont.data": 1}}
        ])

        for v in value:
            r = {}
            if "asset" in v["data"]:
                # r[v["data"]["management"]["managed_object"]].update(v["data"]["asset"])
                r.update(v["data"]["asset"])
            if v["cont"]:
                if "data" in v["cont"][0]:
                    # r[v["data"]["management"]["managed_object"]].update(v["cont"][0]["data"].get("address", {}))
                    r.update(v["cont"][0]["data"].get("address", {}))
            yield v["data"]["management"]["managed_object"], r
