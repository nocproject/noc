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
from collections import defaultdict
from pymongo import ReadPreference
# NOC modules
from .base import BaseReportDataSource
from noc.lib.nosql import get_db


class ReportObjectIfacesStatusStat(BaseReportDataSource):
    """Report for interfaces speed and status count"""

    # ["1G_UP", "1G_DOWN"]
    ATTRS = list("-")
    UNKNOWN = [""] * len(ATTRS)

    @staticmethod
    def load(ids, attributes):
        # @todo Make reports field
        """
        { "_id" : { "managed_object" : 6757 }, "count_in_speed" : 3 }
        { "_id" : { "oper_status" : true, "in_speed" : 10000, "managed_object" : 6757 }, "count_in_speed" : 2 }
        { "_id" : { "oper_status" : true, "in_speed" : 1000000, "managed_object" : 6757 }, "count_in_speed" : 11 }
        { "_id" : { "oper_status" : false, "in_speed" : 1000000, "managed_object" : 6757 }, "count_in_speed" : 62 }
        { "_id" : { "oper_status" : true, "in_speed" : 10000000, "managed_object" : 6757 }, "count_in_speed" : 5 }
        { "_id" : { "oper_status" : false, "in_speed" : 100000, "managed_object" : 6757 }, "count_in_speed" : 1 }
        :return:
        """
        def humanize_speed(speed):
            if not speed:
                return "-"
            for t, n in [
                (1000000, "G"),
                (1000, "M"),
                (1, "k")
            ]:
                if speed >= t:
                    if speed // t * t == speed:
                        return "%d%s" % (speed // t, n)
                    else:
                        return "%.2f%s" % (float(speed) / t, n)
            return str(speed)

        oper = True
        group = {"in_speed": "$in_speed",
                 "managed_object": "$managed_object"}
        if oper:
            group["oper_status"] = "$oper_status"

        match = {"type": "physical"}
        if ids:
            match = {"type": "physical",
                     "managed_object": {"$in": ids}}
        value = get_db()["noc.interfaces"].with_options(read_preference=ReadPreference.SECONDARY_PREFERRED).aggregate([
            {"$match": match},
            {"$group": {"_id": group,
                        "count": {"$sum": 1}}}
        ])
        r = defaultdict(lambda: [""] * len(attributes))
        for v in value:
            c = {
                True: "Up",
                False: "Down",
                None: "-"
            }[v["_id"].get("oper_status", None)] if oper else ""

            if v["_id"].get("in_speed", None):
                c += "/" + humanize_speed(v["_id"]["in_speed"])
            else:
                c += "/-"
            # r[v["_id"]["managed_object"]].append((c, v["count"]))
            if c in attributes:
                r[v["_id"]["managed_object"]][attributes.index(c)] = v["count"]
        return r
        # return dict((v["_id"]["managed_object"], v["count"]) for v in value["result"])
