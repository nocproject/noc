# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## fm.reportreboots
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
## Django modules
from django import forms
from django.db import connection
from django.contrib.admin.widgets import AdminDateWidget
## NOC modules
from noc.lib.app.simplereport import SimpleReport, TableColumn
from noc.fm.models.reboot import Reboot
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


class ReportRebootsApplication(SimpleReport):
    title = _("Reboots")
    form = ReportForm

    def get_data(self, interval, from_date, to_date, **kwargs):
        interval = int(interval)
        if interval:
            ts = datetime.datetime.now() - datetime.timedelta(days=interval)
            match = {
                "ts": {
                    "$gte": ts
                }
            }
        else:
            t0 = datetime.datetime.strptime(from_date, "%d.%m.%Y")
            if not to_date:
                t1 = datetime.datetime.now()
            else:
                t1 = datetime.datetime.strptime(to_date, "%d.%m.%Y") + datetime.timedelta(days=1)
            match = {
                "ts": {
                    "$gte": t0,
                    "$lte": t1
                }
            }
        pipeline = [
            {
                "$match": match
            },
            {"$group": {"_id": "$object", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        data = Reboot._get_collection().aggregate(pipeline)
        data = data["result"]
        # Get managed objects
        ids = [x["_id"] for x in data]
        mo_names = {}  # mo id -> mo name
        cursor = connection.cursor()
        while ids:
            chunk = [str(x) for x in ids[:500]]
            ids = ids[500:]
            cursor.execute("""
                SELECT id, name
                FROM sa_managedobject
                WHERE id IN (%s)""" % ", ".join(chunk))
            mo_names.update(dict(cursor))
        #
        data = [
            (mo_names.get(x["_id"], "---"), x["count"])
            for x in data
        ]

        return self.from_dataset(
            title=self.title,
            columns=[
                _("Managed Object"),
                TableColumn(_("Reboots"), align="right",
                            format="numeric", total="sum")
            ],
            data=data,
            enumerate=True
        )
