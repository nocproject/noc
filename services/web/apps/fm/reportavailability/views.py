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
## Django modules
from django import forms
from django.contrib.admin.widgets import AdminDateWidget
## NOC modules
from noc.fm.models.outage import Outage
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.useraccess import UserAccess
from noc.lib.app.simplereport import SimpleReport, TableColumn, PredefinedReport
from noc.lib.dateutils import total_seconds
from noc.lib.nosql import Q
from noc.core.translation import ugettext as _


class ReportForm(forms.Form):
    interval = forms.ChoiceField(choices=[
        (0, _("Range")),
        (1, _("1 day")),
        (7, _("1 week")),
        (30, _("1 month"))
    ], label=_("Inteval"))
    from_date = forms.CharField(
        widget=AdminDateWidget,
        label=_("From Date"),
        required=False
    )
    to_date = forms.CharField(
        widget=AdminDateWidget,
        label=_("To Date"),
        required=False
    )


class ReportAvailabilityApplication(SimpleReport):
    title = _("Availability")
    form = ReportForm
    predefined_reports = {
        "1d": PredefinedReport(
            _("Availability (1 day)"), {
                "interval": 1
            }
        ),
        "7d": PredefinedReport(
            _("Availability (7 days)"), {
                "interval": 7
            }
        ),
        "30d": PredefinedReport(
            _("Availability (30 day)"), {
                "interval": 30
            }
        )
    }

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

    def get_data(self, request, interval, from_date=None, to_date=None, **kwargs):
        """
        a1 = self.get_availability(1)
        a7 = self.get_availability(7)
        a30 = self.get_availability(30)
        """
        interval = int(interval)
        if not from_date:
            interval = 1
        if not interval:
            if not to_date:
                to_date = datetime.datetime.now().strftime("%d.%m.%Y")
            sub = datetime.datetime.strptime(to_date, "%d.%m.%Y") - \
                  datetime.datetime.strptime(from_date, "%d.%m.%Y")
            interval = sub.days
        a = self.get_availability(interval)
        r = []
        mos = ManagedObject.objects.filter(is_managed=True)
        if not request.user.is_superuser:
            mos = ManagedObject.objects.filter(
                administrative_domain__in=UserAccess.get_domains(request.user))
        for o in mos:
            r += [(
                o.administrative_domain.name,
                o.name,
                o.profile_name,
                o.platform,
                o.address,
                a.get(o.id, 100)
            )]
            """
            a1.get(o.id, 100),
            a7.get(o.id, 100),
            a30.get(o.id, 100)
            """
        return self.from_dataset(
            title=self.title,
            columns=[
                _("Adm. Domain"),
                _("Managed Object"), _("Profile"), _("Platform"), _("Address"),
                TableColumn("%d %s" % (interval, _("Day")), align="right", format="percent"),
            ],
            data=r,
            enumerate=True
        )
