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
## NOC modules
from base import BaseCard
from noc.fm.models.activealarm import ActiveAlarm
from noc.sa.models.servicesummary import SummaryItem


class AlarmHeatCard(BaseCard):
    card_css = [
        "/ui/pkg/leaflet/leaflet.css"
    ]
    card_js = [
        "/ui/pkg/leaflet/leaflet.js",
        "/ui/pkg/card/js/alarmheat.js"
    ]

    default_template_name = "alarmheat"

    def get_data(self):
        return {}
