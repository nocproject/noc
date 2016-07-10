# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## fm.reportalarmdetail application
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
import cStringIO
import csv
## NOC modules
from noc.lib.app.extapplication import ExtApplication, view
from noc.core.translation import ugettext as _
from noc.sa.interfaces.base import StringParameter
from noc.fm.models.archivedalarm import ArchivedAlarm


class ReportAlarmDetailApplication(ExtApplication):
    menu = _("Alarm Detail")
    title = _("Alarm Detail")

    @view("^download/$", method=["GET"], access="launch", api=True,
          validate={
              "from_date": StringParameter(required=True),
              "to_date": StringParameter(required=True),
              "format": StringParameter(choices=["csv", "xlsx"])
          })
    def api_report(self, request, from_date, to_date, format):
        def row(row):
            def qe(v):
                if isinstance(v, unicode):
                    return v.encode("utf-8")
                elif not isinstance(v, str):
                    return str(v)
                else:
                    return v
            return [qe(x) for x in row]

        r = [[
            "ID",
            "FROM_TS",
            "TO_TS",
            "DURATION_SEC",
            "OBJECT_NAME",
            "OBJECT_ADDRESS",
            "OBJECT_PLATFORM",
            "ALARM_CLASS"
        ]]
        q = {
            "timestamp__gte": datetime.datetime.strptime(from_date, "%d.%m.%Y"),
            "timestamp__lte": datetime.datetime.strptime(to_date, "%d.%m.%Y")
        }
        for a in ArchivedAlarm.objects.filter(**q).order_by("timestamp"):
            r += row([
                str(a.id),
                a.timestamp.isoformat(),
                a.clear_timestamp.isoformat(),
                str(a.duration),
                a.managed_object.name,
                a.managed_object.address,
                a.managed_object.platform,
                a.alarm_class.name
            ])
        if format == "csv":
            io = cStringIO.StringIO()
            writer = csv.writer(io)
            writer.writerows(r)
            return self.render_plain_text(io.getvalue(), mimetype="text/csv")
