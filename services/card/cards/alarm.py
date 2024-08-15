# ---------------------------------------------------------------------
# Alarm card handler
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
import operator

# Third-party modules
from mongoengine.errors import DoesNotExist

# NOC modules
from .base import BaseCard
from noc.fm.models.utils import get_alarm
from noc.inv.models.object import Object
from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.archivedalarm import ArchivedAlarm
from noc.sa.models.servicesummary import SummaryItem
from noc.fm.models.alarmseverity import AlarmSeverity
from noc.fm.models.alarmdiagnostic import AlarmDiagnostic
from noc.maintenance.models.maintenance import Maintenance
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
            raise self.NotFoundError()

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
                        cp.insert(0, {"id": o.id, "name": o.name})
                    c = o.container.id if o.container else None
                except DoesNotExist:
                    metrics["error", ("type", "user_not_found")] += 1
                    break
        # Build log
        log = []
        if self.object.log:
            log = [
                {
                    "timestamp": lg.timestamp,
                    "from_status": lg.from_status,
                    "to_status": lg.to_status,
                    "message": lg.message,
                }
                for lg in self.object.log
            ]
        # Build alarm tree
        alarms = self.get_alarms()
        # Service summary
        service_summary = {
            "service": SummaryItem.items_to_dict(self.object.total_services),
            "subscriber": SummaryItem.items_to_dict(self.object.total_subscribers),
        }
        # Maintenance
        m_id = [m for m in self.object.managed_object.affected_maintenances]
        mainteinance = Maintenance.objects.filter(
            is_completed=False,
            start__lte=datetime.datetime.now(),
            stop__gte=datetime.datetime.now(),
            id__in=m_id,
        ).order_by("start")
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
            "tt_system": (
                self.object.managed_object.tt_system.name
                if self.object.managed_object.tt_system
                else None
            ),
            # "tt_system_failed": (
            #     self.object.status == "A"
            #     and not self.object.escalation_tt
            #     and self.object.managed_object.tt_system
            #     and self.object.managed_object.tt_system.is_failed()
            # ),
            "tt_system_failed": False,
            "escalation_ctx": self.object.escalation_ctx,
            "escalation_close_ctx": getattr(self.object, "escalation_close_ctx", None),
        }
        return r

    def get_alarms(self):
        def get_children(ca: "ActiveAlarm", include_groups=True):
            ca._children = []
            for ac in [ActiveAlarm, ArchivedAlarm]:
                for aa in ac.objects.filter(root=ca.id):
                    ca._children += [aa]
                    get_children(aa)
            if include_groups and ca.reference:
                # ca.reference check for OldArchived
                for aa in ActiveAlarm.objects.filter(groups__in=[ca.reference], root__exists=False):
                    ca._children += [aa]
                    get_children(aa, include_groups=False)

        def flatten(ca, r, level):
            ca._level = level
            ca.service_summary = {
                "service": SummaryItem.items_to_dict(ca.direct_services),
                "subscriber": SummaryItem.items_to_dict(ca.direct_subscribers),
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
