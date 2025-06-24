# ---------------------------------------------------------------------
# fm.reportoutages
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
from collections import defaultdict

# Third-party modules
from django import forms
from mongoengine.queryset.visitor import Q

# NOC modules
from noc.fm.models.outage import Outage
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.useraccess import UserAccess
from noc.services.web.base.simplereport import SimpleReport, TableColumn, PredefinedReport
from noc.core.translation import ugettext as _


class ReportForm(forms.Form):
    duration = forms.ChoiceField(
        choices=[
            (0, _("Range")),
            (86400, _("1 day")),
            (7 * 86400, _("1 week")),
            (30 * 86400, _("1 month")),
        ],
        label=_("Duration"),
    )
    from_date = forms.CharField(
        widget=forms.TextInput(attrs={"type": "date"}), label=_("From Date"), required=False
    )
    to_date = forms.CharField(
        widget=forms.TextInput(attrs={"type": "date"}), label=_("To Date"), required=False
    )


class ReportOutagesApplication(SimpleReport):
    title = _("Outages")
    form = ReportForm
    predefined_reports = {
        "1d": PredefinedReport(_("Outages (1 day)"), {"duration": 86400}),
        "7d": PredefinedReport(_("Outages (7 days)"), {"duration": 7 * 86400}),
        "30d": PredefinedReport(_("Outages (30 day)"), {"duration": 30 * 86400}),
    }

    def get_data(self, request, duration, from_date=None, to_date=None, **kwargs):
        now = datetime.datetime.now()
        if not from_date:
            duration = 1
        if int(duration):
            self.logger.info("Use duration\n")
            d = datetime.timedelta(seconds=int(duration))
            b = now - d
            q = Q(start__gte=b) | Q(stop__gte=b) | Q(stop__exists=False)
        else:
            b = datetime.datetime.strptime(from_date, self.ISO_DATE_MASK)
            q = Q(start__gte=b) | Q(stop__gte=b) | Q(stop__exists=False)
            if to_date:
                if from_date == to_date:
                    t1 = datetime.datetime.strptime(
                        to_date, self.ISO_DATE_MASK
                    ) + datetime.timedelta(1)
                else:
                    t1 = datetime.datetime.strptime(to_date, self.ISO_DATE_MASK)
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
            otime[o.object] += (stop - start).total_seconds()
        td = d.total_seconds()
        if not request.user.is_superuser:
            for mo in ManagedObject.objects.exclude(
                administrative_domain__in=UserAccess.get_domains(request.user)
            ):
                if mo.id in otime:
                    otime.pop(mo.id)
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
            downtime = "%02d:%02d:%02d" % ((dt // 3600) % 24, (dt // 60) % 60, dt % 60)
            if dt >= 86400:
                downtime = "%dd %s" % (dt // 86400, downtime)
            if td:
                avail = float(td - dt) * 100 / td
            else:
                avail = 0
            r += [
                (
                    m.name,
                    m.address,
                    m.profile.name,
                    m.platform.name if m.platform else "",
                    _("Yes") if m.is_managed else _("No"),
                    _("Yes") if m.get_status() else _("No"),
                    downtime,
                    avail,
                    len(outages[o]),
                )
            ]

        return self.from_dataset(
            title=self.title,
            columns=[
                _("Managed Object"),
                _("Address"),
                _("Profile"),
                _("Platform"),
                TableColumn(_("Managed"), align="right"),
                TableColumn(_("Status"), align="right"),
                TableColumn(_("Downtime"), align="right"),
                TableColumn(_("Availability"), align="right", format="percent"),
                TableColumn(_("Downs"), align="right", format="integer"),
            ],
            data=r,
            enumerate=True,
        )
