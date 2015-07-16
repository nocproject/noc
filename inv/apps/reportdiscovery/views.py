# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.reportdiscovery
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
## Django modules
from django.db.models import Count
## NOC modules
from noc.lib.app.simplereport import SimpleReport, SectionRow, TableColumn
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.inv.models.interface import Interface
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.inv.models.link import Link
from noc.inv.models.discoveryjob import DiscoveryJob
from noc.sa.models.maptask import MapTask


class ReportDiscoveryApplication(SimpleReport):
    title = "Discovery Summary"

    def get_data(self, **kwargs):
        data = []
        # Managed objects summary
        data += [SectionRow("Managed Objects")]
        d = []
        for p in ManagedObjectProfile.objects.all():
            d += [[
                p.name,
                ManagedObject.objects.filter(object_profile=p).count()
            ]]
        data += sorted(d, key=lambda x: -x[1])
        # Interface summary
        data += [SectionRow("Interfaces")]
        d_count = Interface.objects.count()
        for p in InterfaceProfile.objects.all():
            n = Interface.objects.filter(profile=p).count()
            d += [[p.name, n]]
            d_count -= n
        data += [["-", d_count]]
        data += sorted(d, key=lambda x: -x[1])
        # Links summary
        data += [SectionRow("Links")]
        r = Link._get_collection().aggregate([
            {
                "$group": {
                    "_id": "$discovery_method",
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1}}
        ])
        data += [(x["_id"], x["count"]) for x in r["result"]]
        # Discovery jobs
        data += [SectionRow("Discovery Jobs Statuses")]
        r = DiscoveryJob._get_collection().aggregate([
            {
                "$group": {
                    "_id": "$s",
                    "count": {"$sum": 1}
                }
            }
        ])
        d = []
        for x in r["result"]:
            if x["_id"] == "W":
                nl = DiscoveryJob.objects.filter(
                    status="W",
                    ts__lte=datetime.datetime.now()
                ).count()
                d += [
                    ["Wait (Late)", nl],
                    ["Wait", x["count"] - nl]
                ]
            else:
                d += [[
                    {
                        "W": "Wait",
                        "R": "Run",
                        "S": "Stop",
                        "D": "Disabled",
                        "s": "Suspend"
                    }.get(x["_id"], "-"),
                    x["count"]
                ]]
        data += sorted(d, key=lambda x: -x[1])
        # MapTask summary
        data += [SectionRow("Map Tasks")]
        d = [
            (
                {
                    "W": "Wait",
                    "R": "Running",
                    "C": "Complete",
                    "F": "Failed"
                }.get(x["status"], "-"),
                x["count"]
             )
            for x in MapTask.objects.values("status").annotate(count=Count("status"))]
        data += sorted(d, key=lambda x: -x[1])

        return self.from_dataset(
            title=self.title,
            columns=[
                "",
                TableColumn(
                    "Count", align="right", format="integer",
                    total="sum", total_label="Total"
                )
            ],
            data=data
        )
