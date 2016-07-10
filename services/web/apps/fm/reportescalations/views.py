# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## fm.reportescalations
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
import operator
## Django modules
from django import forms
from django.contrib.admin.widgets import AdminDateWidget
## NOC modules
from noc.lib.app.simplereport import SimpleReport
from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.archivedalarm import ArchivedAlarm
from noc.sa.models.managedobject import ManagedObject
from noc.core.translation import ugettext as _


class ReportForm(forms.Form):
    interval = forms.ChoiceField(choices=[
        (0, _("Range")),
        (1, _("1 day")),
        (7, _("1 week")),
        (30, _("1 month"))
    ])
    from_date = forms.CharField(
        widget=AdminDateWidget,
        required=False
    )
    to_date = forms.CharField(
        widget=AdminDateWidget,
        required=False
    )


class ReportEscalationsApplication(SimpleReport):
    title = _("Escalations")
    form = ReportForm

    def get_data(self, interval, from_date, to_date, **kwargs):
        interval = int(interval)
        if interval:
            ts = datetime.datetime.now() - datetime.timedelta(days=interval)
            q = {
                "timestamp": {
                    "$gte": ts
                }
            }
        else:
            t0 = datetime.datetime.strptime(from_date, "%d.%m.%Y")
            if not to_date:
                t1 = datetime.datetime.now()
            else:
                t1 = datetime.datetime.strptime(to_date, "%d.%m.%Y") + datetime.timedelta(days=1)
            q = {
                "timestamp": {
                    "$gte": t0,
                    "$lte": t1
                }
            }
        q["escalation_tt"] = {
            "$exists": True
        }
        data = []
        for ac in (ActiveAlarm, ArchivedAlarm):
            for d in ac._get_collection().find(q):
                mo = ManagedObject.get_by_id(d["managed_object"])
                data += [(
                    d["timestamp"],
                    d["escalation_ts"],
                    mo.name,
                    mo.segment.name,
                    mo.platform,
                    mo.address,
                    d["escalation_tt"]
                )]
        data = sorted(data, key=operator.itemgetter(0))
        return self.from_dataset(
            title=self.title,
            columns=[
                _("Timestamp"),
                _("Escalation Timestamp"),
                _("Managed Object"),
                _("Segment"),
                _("Platform"),
                _("Address"),
                _("TT")
            ],
            data=data,
            enumerate=True
        )
