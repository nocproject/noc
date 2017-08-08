# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# fm.reportettsystemstat
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
import time
# Django modules
from django import forms
from django.contrib.admin.widgets import AdminDateWidget
# NOC modules
from noc.lib.app.simplereport import SimpleReport, PredefinedReport, SectionRow
from noc.core.clickhouse.connect import connection
from noc.fm.models.ttsystem import TTSystem
from noc.core.translation import ugettext as _


class ReportForm(forms.Form):
    interval = forms.ChoiceField(choices=[
        (0, _("Range")),
        (1, _("1 day")),
        (7, _("1 week")),
        (30, _("1 month"))
    ], label=_("Interval"))
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


class ReportTTSystemStatApplication(SimpleReport):
    title = _("TT system statistics")
    form = ReportForm
    predefined_reports = {
        "1d": PredefinedReport(
            _("TTSystem Stat (1 day)"), {
                "interval": 1
            }
        ),
        "7d": PredefinedReport(
            _("TTSystem Stat (7 days)"), {
                "interval": 7
            }
        ),
        "30d": PredefinedReport(
            _("TTSystem Stat (30 day)"), {
                "interval": 30
            }
        )
    }

    def get_data(self, request, interval, from_date=None, to_date=None, **kwargs):
        # Date Time Block
        if from_date:
            from_date = datetime.datetime.strptime(from_date, "%d.%m.%Y")
        elif interval:
            from_date = datetime.datetime.now() - datetime.timedelta(days=int(interval))
        else:
            from_date = datetime.datetime.now() - datetime.timedelta(days=1)

        if to_date:
            to_date = datetime.datetime.strptime(to_date, "%d.%m.%Y")
            if from_date == to_date:
                to_date = from_date + datetime.timedelta(days=1)
        elif interval:
            to_date = from_date + datetime.timedelta(days=int(interval))
        else:
            to_date = from_date + datetime.timedelta(days=1)

        columns = [_("Server"), _("Service"), _("Request count"), _("Success request count"),
                   _("Failed request count"), _("Success request (%)"),
                   _("Q1 (ms)"), _("Q2 (ms)"), _("Q3 (ms)"), _("p95 (ms)"), _("max (ms)")]
        ts_from_date = time.mktime(from_date.timetuple())
        ts_to_date = time.mktime(to_date.timetuple())

        tt_systems = TTSystem.objects.filter().scalar("name")
        # Manged Object block

        q1 = """select server, service, count(), round(quantile(0.25)(duration), 0)/1000 as q1, 
                                        round(quantile(0.5)(duration), 0)/1000 as q2, 
                                        round(quantile(0.75)(duration), 0)/1000 as q3, 
                                        round(quantile(0.95)(duration),0)/1000 as p95, 
                                        round(max(duration),0)/1000 as max from span where %s
                                        group by server, service"""

        q2 = """select server, service, error_code, count(), avg(duration) 
                from span where %s group by server, service, error_code"""

        q_where = ["server IN ('%s')" % "', '".join(tt_systems)]
        # q_where = ["managed_object IN (%s)" % ", ".join(mo_bi_dict.keys())]
        q_where += ["(date >= toDate(%d)) AND (ts >= toDateTime(%d) AND ts <= toDateTime(%d))" % (ts_from_date,
                                                                                                  ts_from_date,
                                                                                                  ts_to_date)]

        ch = connection()
        query = q1 % " and ".join(q_where)
        # (server, service)
        tt_s = {}

        for row in ch.execute(query):
            tt_s[(row[0], row[1])] = [row[2]] + [0, 0, 0] + row[3:]

        query = q2 % " and ".join(q_where)
        for row in ch.execute(query):
            if row[2] == "0":
                tt_s[(row[0], row[1])][1] = row[3]
            else:
                tt_s[(row[0], row[1])][2] += int(row[3])

        r = []
        r += [SectionRow(name="Report from %s to %s" % (from_date.strftime("%d.%m.%Y %H:%M"),
                                                        to_date.strftime("%d.%m.%Y %H:%M")))]
        for l in sorted(tt_s):
            data = list(l)
            data += tt_s[l]
            data[5] = round((float(data[3])/float(data[2]))*100.0, 2)
            r += [data]

        return self.from_dataset(
            title=self.title,
            columns=columns,
            data=r,
            enumerate=True
        )
