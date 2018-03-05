# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Alarm card handler
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import datetime
import operator
# NOC modules
from .base import BaseCard
from noc.fm.models.utils import get_alarm
from noc.inv.models.object import Object
from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.archivedalarm import ArchivedAlarm
from noc.sa.models.servicesummary import SummaryItem
from noc.fm.models.alarmseverity import AlarmSeverity
from noc.fm.models.alarmdiagnostic import AlarmDiagnostic
from noc.maintenance.models.maintenance import Maintenance, MaintenanceObject
from noc.core.perf import metrics


class AlarmCard(BaseCard):
    name = "alarm"
    default_template_name = "alarm"

    def dereference(self, id):
        a = get_alarm(id)
        if self.current_user.is_superuser:
            return a
        elif set(self.get_user_domains()) & set(a.adm_path):
            return a
        else:
            metrics["error", ("type", "no_such_alarm")] += 1
            return None

    def get_data(self):
        if not self.object:
            return None
        # Get container path
        cp = []
        if self.object.managed_object.container:
            c = self.object.managed_object.container.id
            while c:
                try:
                    o = Object.objects.get(id=c)
                    # @todo: Address data
                    if o.container:
                        cp.insert(0, {
                            "id": o.id,
                            "name": o.name
                        })
                    c = o.container
                except Object.DoesNotExist:
                    metrics["error", ("type", "user_not_found")] += 1
                    break
        # Build log
        log = []
        if self.object.log:
            log = [
                {
                    "timestamp": l.timestamp,
                    "from_status": l.from_status,
                    "to_status": l.to_status,
                    "message": l.message
                } for l in self.object.log
            ]
        # Build alarm tree
        alarms = self.get_alarms()
        # Service summary
        service_summary = {
            "service": SummaryItem.items_to_dict(self.object.total_services),
            "subscriber": SummaryItem.items_to_dict(self.object.total_subscribers)
        }
        # Maintenance
        mainteinance = Maintenance.objects.filter(
            is_completed=False,
            start__lte=datetime.datetime.now(),
            affected_objects__in=[
                MaintenanceObject(object=self.object.managed_object)
            ]
        )
        mo = self.object.managed_object
        # Build result
        r = {
            "id": self.object.id,
            "alarm": self.object,
            "severity": AlarmSeverity.get_severity(self.object.severity),
            "managed_object": self.object.managed_object,
            "timestamp": self.object.timestamp,
            "duration": self.object.display_duration,
            "subject": self.object.subject,
            "body": self.object.body,
            "container_path": cp,
            "log": log,
            "service_summary": service_summary,
            "alarms": alarms,
            "diagnostic": AlarmDiagnostic.get_diagnostics(self.object),
            "maintenance": mainteinance,
            "lon": mo.x,
            "lat": mo.y,
            "zoom": mo.default_zoom,
            "tt_system": self.object.managed_object.tt_system.name if self.object.managed_object.tt_system else None,
            "tt_system_failed": (self.object.status == "A" and
                                 not self.object.escalation_tt and
                                 self.object.managed_object.tt_system and
                                 self.object.managed_object.tt_system.is_failed()),
            "escalation_ctx": self.object.escalation_ctx,
            "escalation_close_ctx": getattr(self.object, "escalation_close_ctx", None)
        }
        return r

    def get_alarms(self):
        def get_children(ca):
            ca._children = []
            for ac in [ActiveAlarm, ArchivedAlarm]:
                for a in ac.objects.filter(root=ca.id):
                    ca._children += [a]
                    get_children(a)

        def flatten(ca, r, level):
            ca._level = level
            ca.service_summary = {
                "service": SummaryItem.items_to_dict(ca.direct_services),
                "subscriber": SummaryItem.items_to_dict(ca.direct_subscribers)
            }
            r += [ca]
            if hasattr(ca, "_children"):
                for c in sorted(ca._children, key=operator.attrgetter("timestamp")):
                    flatten(c, r, level + 1)

        # Step upwards
        r = self.object
        a = r
        while r and r.root:
            a = get_alarm(r.root)
            if a:
                a._children = [r]
                r = a
            else:
                break
        # Fill children
        get_children(self.object)
        # Flatten
        result = []
        flatten(a, result, 0)
        return result
