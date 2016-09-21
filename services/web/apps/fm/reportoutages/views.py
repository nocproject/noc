# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## fm.reportoutages
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
from collections import defaultdict
## Django modu;es
from django import forms
from django.contrib.admin.widgets import AdminDateWidget
## NOC modules
from noc.fm.models.outage import Outage
from noc.sa.models.managedobject import ManagedObject
from noc.lib.app.simplereport import SimpleReport, TableColumn
from noc.lib.dateutils import total_seconds
from noc.lib.nosql import Q
from noc.core.translation import ugettext as _


class ReportForm(forms.Form):
    duration = forms.ChoiceField(choices=[
        (0, _("Range")),
        (86400, _("1 day")),
        (7 * 86400, _("1 week")),
        (30 * 86400, _("1 month"))
    ])
    from_date = forms.CharField(
        widget=AdminDateWidget,
        required=False
    )
    to_date = forms.CharField(
        widget=AdminDateWidget,
        required=False
    )


class ReportOutagesApplication(SimpleReport):
    title = _("Outages")
    form = ReportForm

    def get_data(self, duration, from_date, to_date, **kwargs):
        now = datetime.datetime.now()
        if int(duration):
            self.logger.info("Use duration\n")
            d = datetime.timedelta(seconds=int(duration))
            b = now - d
            q = Q(start__gte=b) | Q(stop__gte=b) | Q(stop__exists=False)
        else:
            b = datetime.datetime.strptime(from_date, "%d.%m.%Y")
            q = Q(start__gte=b) | Q(stop__gte=b) | Q(stop__exists=False)
            if to_date:
                t1 = datetime.datetime.strptime(to_date, "%d.%m.%Y")
            else:
                t1 = now
            q &= Q(start__lte=t1) | Q(stop__lte=t1)
            d = datetime.timedelta(seconds=int((t1 - b).total_seconds()))
        outages = defaultdict(list)
        otime = defaultdict(int)
        for o in Outage.objects.filter(q):
            start = max(o.start, b)
            stop = o.stop if o.stop else now
            outages[o.object] += [o]
            otime[o.object] += total_seconds(stop - start)
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
            m = mo.get(o)
            if not m:
                continue  # Hanging Outage
            dt = min(td, otime[o])
            downtime = "%02d:%02d:%02d" % (
                (dt // 3600) % 24,
                (dt // 60) % 60,
                dt % 60
            )
            if dt >= 86400:
                downtime = "%dd %s" % (dt // 86400, downtime)
            r += [(
                m.name,
                m.address,
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
                _("Managed Object"), _("Address"), _("Profile"), _("Platform"),
                TableColumn(_("Managed"), format="bool"),
                TableColumn(_("Status"), format="bool"),
                TableColumn(_("Downtime"), align="right"),
                TableColumn(_("Availability"), align="right", format="percent"),
                TableColumn(_("Downs"), align="right", format="integer")
            ],
            data=r,
            enumerate=True
        )
