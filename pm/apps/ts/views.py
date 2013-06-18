# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## pm.ts application
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import time
## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.pm.models.ts import PMTS


class PMTSApplication(ExtDocApplication):
    """
    PMTS application
    """
    title = "Time Series"
    menu = "Time Series"
    model = PMTS
    query_fields = ["name", "check__name"]

    def field_last_timestamp(self, o):
        if not hasattr(o, "_last_measure"):
            o._last_measure = o.last_measure
        return o._last_measure[0]

    def field_last_value(self, o):
        if not hasattr(o, "_last_measure"):
            o._last_measure = o.last_measure
        return o._last_measure[1]

    @view(url="^data/", method=["GET"], api=True, access="data")
    def api_data(self, request):
        """
        Accepts GET request
            begin -- start timestamp
            end -- end timestamp
            ts -- multiple ts id
        Return data in form
        {
            begin: timestamp,
            end: timestamp
            data: {
                ts id: [(timestamp, value) ..... ]
            }
        :param request:
        :return:
        """
        t = int(time.time())
        end = int(request.GET.get("end", t))
        begin = int(request.GET.get("begin", end - 3600))
        data = {}
        for ts in [int(x) for x in request.GET.getlist("ts")]:
            t = PMTS.objects.filter(ts_id=ts).first()
            if not t:
                continue
            data[ts] = [
                (timestamp, value)
                for _, timestamp, value
                in t.iwindow(begin, end)
            ]
        return {
            "begin": begin,
            "end": end,
            "data": data
        }
