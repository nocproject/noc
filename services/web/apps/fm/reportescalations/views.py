# ----------------------------------------------------------------------
#  fm.reportescalations
# ----------------------------------------------------------------------
#  Copyright (C) 2007-2025 The NOC Project
#  See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
import operator

# Third-party modules
from django import forms

# NOC modules
from noc.services.web.base.simplereport import SimpleReport, PredefinedReport
from noc.sa.models.useraccess import UserAccess
from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.archivedalarm import ArchivedAlarm
from noc.sa.models.managedobject import ManagedObject
from noc.core.translation import ugettext as _


class ReportForm(forms.Form):
    interval = forms.ChoiceField(
        choices=[(0, _("Range")), (1, _("1 day")), (7, _("1 week")), (30, _("1 month"))],
        label=_("Interval"),
    )
    from_date = forms.CharField(
        widget=forms.TextInput(attrs={"type": "date"}), label=_("From Date"), required=False
    )
    to_date = forms.CharField(
        widget=forms.TextInput(attrs={"type": "date"}), label=_("To Date"), required=False
    )


class ReportEscalationsApplication(SimpleReport):
    title = _("Escalations")
    form = ReportForm
    predefined_reports = {
        "1d": PredefinedReport(_("Escalations (1 day)"), {"interval": 1}),
        "7d": PredefinedReport(_("Escalations (7 days)"), {"interval": 7}),
        "30d": PredefinedReport(_("Escalations (30 day)"), {"interval": 30}),
    }

    def get_data(self, request, interval, from_date=None, to_date=None, **kwargs):
        interval = int(interval)
        if not from_date:
            interval = 1
        if interval:
            ts = datetime.datetime.now() - datetime.timedelta(days=interval)
            q = {"timestamp": {"$gte": ts}}
        else:
            t0 = datetime.datetime.strptime(from_date, self.ISO_DATE_MASK)
            if not to_date:
                t1 = datetime.datetime.now()
            else:
                t1 = datetime.datetime.strptime(to_date, self.ISO_DATE_MASK) + datetime.timedelta(
                    days=1
                )
            q = {"timestamp": {"$gte": t0, "$lte": t1}}
        q["escalation_tt"] = {"$exists": True}
        if not request.user.is_superuser:
            q["adm_path"] = {"$in": UserAccess.get_domains(request.user)}
        data = []
        for ac in (ActiveAlarm, ArchivedAlarm):
            for d in ac._get_collection().find(q):
                mo = ManagedObject.get_by_id(d["managed_object"])
                if not mo:
                    continue
                data += [
                    (
                        d["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
                        d["escalation_ts"].strftime("%Y-%m-%d %H:%M:%S"),
                        mo.name.split("#", 1)[0],
                        mo.address,
                        mo.platform,
                        mo.segment.name,
                        d["escalation_tt"],
                        sum(ss["summary"] for ss in d["total_objects"]),
                        sum(ss["summary"] for ss in d["total_subscribers"]),
                    )
                ]
        data = sorted(data, key=operator.itemgetter(0))
        return self.from_dataset(
            title=self.title,
            columns=[
                _("Timestamp"),
                _("Escalation Timestamp"),
                _("Managed Object"),
                _("Address"),
                _("Platform"),
                _("Segment"),
                _("TT"),
                _("Objects"),
                _("Subscribers"),
            ],
            data=data,
            enumerate=True,
        )
