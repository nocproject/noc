# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alarm heatmap
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
import operator
## Third-party modules
import cachetools
## NOC modules
from base import BaseCard
from noc.fm.models.activealarm import ActiveAlarm
from noc.inv.models.object import Object
from noc.sa.models.servicesummary import ServiceSummary, SummaryItem


class AlarmHeatCard(BaseCard):
    name = "alarmheat"
    card_css = [
        "/ui/pkg/leaflet/leaflet.css",
        "/ui/card/css/alarmheat.css"
    ]
    card_js = [
        "/ui/pkg/leaflet/leaflet.js",
        "/ui/pkg/leaflet.heat/leaflet-heat.js",
        "/ui/card/js/alarmheat.js"
    ]

    default_template_name = "alarmheat"

    def get_data(self):
        return {}

    def get_object_coords(self, mo):
        """
        Get managed object's coordinates
        """
        c = mo.container
        while c:
            x = c.get_data("geopoint", "x")
            y = c.get_data("geopoint", "y")
            if x and y:
                return x, y
            if c.container:
                try:
                    c = Object.objects.get(id=c.container)
                except Object.DoesNotExist:
                    break
            else:
                break
        return None, None

    def get_ajax_data(self, **kwargs):
        def update_dict(d, s):
            for k in s:
                if k in d:
                    d[k] += s[k]
                else:
                    d[k] = s[k]

        alarms = []
        services = {}
        subscribers = {}
        for a in ActiveAlarm.objects.all():
            mo = a.managed_object
            x, y = self.get_object_coords(mo)
            w = 0
            s_sub = SummaryItem.items_to_dict(a.direct_subscribers)
            s_service = SummaryItem.items_to_dict(a.direct_services)
            if x and y:
                w = ServiceSummary.get_weight({
                    "subscriber": s_sub,
                    "service": s_service
                })
            alarms += [{
                "alarm_id": str(a.id),
                "managed_object": mo.name,
                "x": x,
                "y": y,
                "w": max(w, 1)
            }]
            update_dict(services, s_service)
            update_dict(subscribers, s_sub)

        return {
            "alarms": alarms,
            "summary": self.f_glyph_summary({
                "service": services,
                "subscriber": subscribers
            })
        }
