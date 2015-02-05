# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## fm.reportavailability
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
from collections import defaultdict
## NOC modules
from noc.fm.models.outage import Outage
from noc.sa.models.managedobject import ManagedObject
from noc.lib.app.simplereport import SimpleReport, TableColumn
from noc.lib.dateutils import total_seconds
from noc.lib.nosql import Q


class ReportAvailabilityApplication(SimpleReport):
    title = "Availability"

    def get_availability(self, days):
        now = datetime.datetime.now()
        d = datetime.timedelta(days=days)
        b = now - d
        outages = defaultdict(int)
        q = Q(start__gte=b) | Q(stop__gte=b) | Q(stop__exists=False)
        for o in Outage.objects.filter(q):
            start = max(o.start, b)
            stop = o.stop if o.stop else now
            outages[o.object] += total_seconds(stop - start)
        td = total_seconds(d)
        # Normalize to percents
        return dict((o, (td - outages[o]) * 100.0 / td) for o in outages)

    def get_data(self, **kwargs):
        a1 = self.get_availability(1)
        a7 = self.get_availability(7)
        a30 = self.get_availability(30)
        r = []
        for o in ManagedObject.objects.filter(is_managed=True):
            r += [(
                o.name,
                o.profile_name,
                o.platform,
                a1.get(o.id, 100),
                a7.get(o.id, 100),
                a30.get(o.id, 100)
            )]
        return self.from_dataset(
            title=self.title,
            columns=[
                "Object", "Profile", "Platform",
                TableColumn("24h", align="right", format="percent"),
                TableColumn("7d", align="right", format="percent"),
                TableColumn("30d", align="right", format="percent")
            ],
            data=r
        )
