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
from noc.lib.app.simplereport import SimpleReport, TableColumn, PredefinedReport, SectionRow
from noc.lib.dateutils import total_seconds
from noc.lib.nosql import Q
from pymongo import ReadPreference
from noc.core.translation import ugettext as _


class ReportForm(forms.Form):
    """
    interval = forms.ChoiceField(choices=[
        (0, _("Range")),
        (1, _("last day")),
        (7, _("last week")),
        (30, _("last month"))
    ], label=_("Inteval"))
    """
    from_date = forms.CharField(
        widget=AdminDateWidget,
        label=_("From Date"),
        required=True
    )
    to_date = forms.CharField(
        widget=AdminDateWidget,
        label=_("To Date"),
        required=False
    )
    skip_avail = forms.BooleanField(
        label=_("Skip full available"),
        required=False
    )
    skip_zero_avail = forms.BooleanField(
        label=_("Skip zero available"),
        required=False
    )


class ReportAvailabilityApplication(SimpleReport):
    title = _("Availability")
    form = ReportForm
    predefined_reports = {
        "1d": PredefinedReport(
            _("Availability (last day)"), {
                "interval": 1
            }
        ),
        "7d": PredefinedReport(
            _("Availability (last week)"), {
                "interval": 7
            }
        ),
        "30d": PredefinedReport(
            _("Availability (last month)"), {
                "interval": 30
            }
        )
    }

    @staticmethod
    def get_availability(start_date, stop_date, skip_zero_avail=False):
        now = datetime.datetime.now()
        d = stop_date
        b = start_date
        outages = defaultdict(list)
        td = total_seconds(d - b)
        q = Q(start__gte=b) | Q(stop__gte=b) | Q(stop__exists=False)
        for o in Outage.objects.filter(q):
            start = max(o.start, b)
            stop = o.stop if o.stop else d
            if total_seconds(stop - start) == td and skip_zero_avail:
                continue
            outages[o.object] += [total_seconds(stop - start)]
        # Normalize to percents
        return dict((o, ((td - sum(outages[o])) * 100.0 / td, int(sum(outages[o])), len(outages[o]))) for o in outages)

    def get_data(self, request, interval=1, from_date=None, to_date=None,
                 skip_avail=False, skip_zero_avail=False, **kwargs):
        """
        a1 = self.get_availability(1)
        a7 = self.get_availability(7)
        a30 = self.get_availability(30)
        """

        if not from_date:
            from_date = datetime.datetime.now() - datetime.timedelta(days=interval)
        else:
            from_date = datetime.datetime.strptime(from_date, "%d.%m.%Y")

        if not to_date or from_date == to_date:
            to_date = from_date + datetime.timedelta(days=1)
        else:
            to_date = datetime.datetime.strptime(to_date, "%d.%m.%Y") + datetime.timedelta(days=1)

        a = self.get_availability(start_date=from_date, stop_date=to_date, skip_zero_avail=skip_zero_avail)
        r = [SectionRow("Report from %s to %s" % (from_date, to_date))]
        mos = ManagedObject.objects.filter(is_managed=True)

        if not request.user.is_superuser:
            mos = mos.filter(
                administrative_domain__in=UserAccess.get_domains(request.user))
        if skip_avail:
            mos = mos.filter(id__in=list(a))
        for o in mos:
            s = [
                o.administrative_domain.name,
                o.name,
                o.address,
                o.profile_name
            ]
            s.extend(a.get(o.id, (100, 0, 0)))
            r += [s]
            """
            a1.get(o.id, 100),
            a7.get(o.id, 100),
            a30.get(o.id, 100)
            """
        print r
        return self.from_dataset(
            title=self.title,
            columns=[
                _("Adm. Domain"), _("Managed Object"), _("Address"), _("Profile"),
                TableColumn(_("Avail"), align="right", format="percent"),
                TableColumn(_("Total avail (sec)"), align="right", format="numeric"),
                _("Count outages")
            ],
            data=r,
            enumerate=True
        )
