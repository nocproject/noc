# ----------------------------------------------------------------------
# ReportObjectIfacesTypeStat datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from collections import defaultdict
from pymongo import ReadPreference

# NOC modules
from .base import BaseReportColumn
from noc.core.mongo.connection import get_db


class ReportObjectIfacesStatusStat(BaseReportColumn):
    """Report for interfaces speed and status count"""

    name = "reportifacesstatusstat"
    # ["1G_UP", "1G_DOWN"]
    # ATTRS = list("-")
    ATTRS = ["Up/10G", "Up/1G", "Up/100M", "Up/10M", "Down/-", "-"]
    unknown_value = ([""] * len(ATTRS),)

    def extract(self):
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
            for t, n in [(1000000, "G"), (1000, "M"), (1, "k")]:
                if speed >= t:
                    if speed // t * t == speed:
                        return "%d%s" % (speed // t, n)
                    return "%.2f%s" % (float(speed) / t, n)
            return str(speed)

        oper = True
        group = {"in_speed": "$in_speed", "managed_object": "$managed_object"}
        if oper:
            group["oper_status"] = "$oper_status"

        match = {"type": "physical"}
        if self.sync_ids:
            match = {"type": "physical", "managed_object": {"$in": self.sync_ids}}
        value = (
            get_db()["noc.interfaces"]
            .with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
            .aggregate(
                [{"$match": match}, {"$group": {"_id": group, "count": {"$sum": 1}}}],
                allowDiskUse=True,
            )
        )
        r = defaultdict(lambda: [""] * len(self.ATTRS))
        # @todo Fix Down
        for v in value:
            c = (
                {True: "Up", False: "Down", None: "-"}[v["_id"].get("oper_status", None)]
                if oper
                else ""
            )

            if v["_id"].get("in_speed", None):
                c += "/" + humanize_speed(v["_id"]["in_speed"])
            else:
                c += "/-"
            # r[v["_id"]["managed_object"]].append((c, v["count"]))
            if c in self.ATTRS:
                r[v["_id"]["managed_object"]][self.ATTRS.index(c)] = v["count"]
        for val in r:
            yield val, r[val]
