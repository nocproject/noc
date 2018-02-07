# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Object card handler
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
import datetime
import operator
from base import BaseCard
from noc.inv.models.object import Object
from noc.sa.models.managedobject import ManagedObject
from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.uptime import Uptime
from noc.fm.models.outage import Outage
from noc.core.perf import metrics
from noc.pm.models.metricscope import MetricScope
from noc.pm.models.metrictype import MetricType


class ObjectCard(BaseCard):
    name = "object"
    default_template_name = "object"
    model = Object
    def get_data(self):
        # Get path
        path = [{
            "id": self.object.id,
            "name": self.object.name
        }]
        c = self.object.container
        while c:
            try:
                c = Object.get_by_id(c)
                if not c:
                    break
                if c.name != "Root":
                    path.insert(0, {
                        "id": c.id,
                        "name": c.name
                    })
                c = c.container
            except Object.DoesNotExist:
                metrics["error", ("type", "no_such_object")] += 1
                break

         # Get children
        children = []

        # Metrics
        #print self.get_metrics(ManagedObject.objects.filter(container=self.objec                                                                                       t.id))

        for o in ManagedObject.objects.filter(container=self.object.id):


            if not self.object:
                return None


            # Alarms
            now = datetime.datetime.now()
            # Get object status and uptime
            alarms = list(ActiveAlarm.objects.filter(managed_object=o.id))
            current_start = None
            duration = None
            uptime = Uptime.objects.filter(
                object=o.id,
                stop=None
            ).first()
            if uptime:
                current_start = uptime.start
            else:
                current_state = "down"
                outage = Outage.objects.filter(
                    object=o.id,
                    stop=None
                ).first()
                if outage:
                    current_start = outage.start
            if current_start:
                duration = now - current_start

            # Alarms detailed information
            alarm_list = []
            for alarm in alarms:
                alarm_list += [{
                    "id": alarm.id,
                    "timestamp": alarm.timestamp,
                    "duration": now - alarm.timestamp,
                    "subject": alarm.subject
                }]
            alarm_list = sorted(alarm_list, key=operator.itemgetter("timestamp"))

            children += [{
                "id": o.id,
                "name": o.name,
                "address": o.address,
                "platform": o.platform.name if o.platform else "Unknown",
                "version": o.version.version if o.version else "",
                "description": o.description,
                "object_profile": o.object_profile.id,
                "object_profile_name": o.object_profile.name,
                "segment": o.segment,
                #
                "current_state": current_state,
                # Start of uptime/downtime
                "current_start": current_start,
                # Current uptime/downtime
                "current_duration": duration,
                "alarms": alarm_list
            }]

        return {
            "object": self.object,
            "path": path,
            "location": self.object.get_data("address", "text"),
            "id": self.object.id,
            "children": children
        }

