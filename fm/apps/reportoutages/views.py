# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## fm.reportoutages
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
from collections import defaultdict
## Django modu;es
from django import forms
## NOC modules
from noc.fm.models.outage import Outage
from noc.sa.models.managedobject import ManagedObject
from noc.lib.app.simplereport import SimpleReport, TableColumn
from noc.lib.dateutils import total_seconds
from noc.lib.nosql import Q


class ReportForm(forms.Form):
    duration = forms.ChoiceField(choices=[
        (86400, "1 day"),
        (7 * 86400, "1 week"),
        (30 * 86400, "1 month")
    ])


class ReportOutagesApplication(SimpleReport):
    title = "Outages"

    form = ReportForm

    def get_data(self, duration, **kwargs):
        now = datetime.datetime.now()
        d = datetime.timedelta(seconds=int(duration))
        b = now - d
        outages = defaultdict(list)
        otime = defaultdict(int)
        q = Q(start__gte=b) | Q(stop__gte=b) | Q(stop__exists=False)
        for o in Outage.objects.filter(q):
            start = max(o.start, b)
            stop = o.stop if o.stop else now
            outages[o.object] += [o]
            otime[o.object] = total_seconds(stop - start)
        td = total_seconds(d)
        # Load managed objects
        mos = list(otime)
        chunk = 500
        mo = {}
        while mos:
            for o in ManagedObject.objects.filter(id__in=mos[:chunk]):
                mo[o.id] = o
            mos = mos[chunk:]
        r = []
        for o in sorted(otime, key=lambda x: -otime[x]):
            m = mo[o]
            dt = otime[o]
            downtime = "%02d:%02d:%02d" % (
                (dt // 3600) % 24,
                (dt // 60) % 60,
                dt % 60
            )
            if dt >= 86400:
                downtime = "%dd %s" % (dt // 86400, downtime)
            r += [(
                m.name,
                m.profile_name,
                m.platform,
                m.is_managed,
                m.get_status(),
                downtime,
                float(td - dt) * 100 / td,
                len(outages[o])
            )]

        return self.from_dataset(
            title=self.title,
            columns=[
                "Object", "Profile", "Platform",
                TableColumn("Managed", format="bool"),
                TableColumn("Status", format="bool"),
                TableColumn("Downtime", align="right"),
                TableColumn("Availability", align="right", format="percent"),
                TableColumn("Downs", align="right", format="integer")
            ],
            data=r,
            enumerate=True
        )
