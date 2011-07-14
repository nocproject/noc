# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## FM Events and Alarms Hierarchy Report
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app.reportapplication import ReportApplication
from noc.fm.models import EventClass, EventClassCategory,\
                          AlarmClass, AlarmClassCategory,\
                          EventClassificationRule


class HierarchyReportAppplication(ReportApplication):
    """
    FM Events and Alarms hierarchy
    """
    title = "Events and Alarm Hierarchy"

    def report_html(self):
        # Event classes
        ec = []
        ne = 0
        for cc in EventClassCategory.objects.order_by("name"):
            e = EventClass.objects.filter(category=cc.id).order_by("name")
            if not e:
                continue
            p = cc.name.split(" | ")
            ec += [(len(p) * 24, cc.name, None)]
            ec += [(-1, c,
                    EventClassificationRule.objects.filter(event_class=c.id))
                    for c in e]
            ne += len(e)
        ncr = 0
        for _, _, r in ec:
            if r:
                ncr += len(r)
        # Alarm classes
        ac = []
        na = 0
        for cc in AlarmClassCategory.objects.order_by("name"):
            a = AlarmClass.objects.filter(category=cc.id).order_by("name")
            if not a:
                continue
            p = cc.name.split(" | ")
            ac += [(len(p) * 24, cc.name)]
            ac += [(-1, c) for c in a]
            na += len(a)
        return self.render_template("data.html",
                                    event_classes=ec, alarm_classes=ac,
                                    ne=ne, na=na, ncr=ncr)
