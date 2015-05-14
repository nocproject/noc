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
## NOC modules
from noc.lib.app.simplereport import SimpleReport, TableColumn
from noc.fm.models.reboot import Reboot


class ReportForm(forms.Form):
    interval = forms.ChoiceField(choices=[
        (1, "1 day"),
        (7, "1 week"),
        (30, "1 month")
    ])


class ReportRebootsApplication(SimpleReport):
    title = "Reboots"
    form = ReportForm

    def get_data(self, interval, **kwargs):
        interval = int(interval)
        ts = datetime.datetime.now() - datetime.timedelta(days=interval)
        pipeline = [
            {
                "$match": {
                    "ts": {"$gte": ts}
                }
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
            mo_names = dict(cursor)
        #
        data = [
            (mo_names.get(x["_id"], "---"), x["count"])
            for x in data
        ]

        return self.from_dataset(
            title=self.title,
            columns=[
                "Managed Object",
                TableColumn("Reboots", align="right", format="numeric")
            ],
            data=data,
            enumerate=True
        )
