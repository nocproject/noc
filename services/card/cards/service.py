# ---------------------------------------------------------------------
# Service card handler
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
import operator

# NOC modules
from .base import BaseCard
from noc.sa.models.service import Service
from noc.fm.models.activealarm import ActiveAlarm
from noc.maintenance.models.maintenance import Maintenance


class ServiceCard(BaseCard):
    name = "service"
    default_template_name = "service"
    model = Service

    def get_data(self):
        now = datetime.datetime.now()
        # Build service tree
        services = self.get_services()
        # Get interface and managed object
        interface = self.get_interface()
        managed_object = interface.managed_object if interface else None
        managed_obect_status = None
        alarms = []
        errors = []
        warnings = []
        maintenance = []
        if managed_object:
            alarms = list(ActiveAlarm.objects.filter(managed_object=managed_object.id))
            if managed_object.get_status():
                if alarms:
                    managed_obect_status = "alarm"
                else:
                    managed_obect_status = "up"
            else:
                managed_obect_status = "down"
                errors += ["Object is down"]
            interface.speed = max([interface.in_speed or 0, interface.out_speed or 0]) / 1000
            if not interface.full_duplex:
                errors += ["Half-Duplex"]
            # Maintenance
            m_id = managed_object.get_active_maintenances()
            for m in Maintenance.objects.filter(
                id__in=m_id,
                is_completed=False,
                start__lte=now + datetime.timedelta(hours=1),
            ):
                maintenance += [
                    {
                        "maintenance": m,
                        "id": m.id,
                        "subject": m.subject,
                        "start": m.start,
                        "stop": m.stop,
                        "in_progress": m.start <= now,
                    }
                ]

        # Build warnings
        # Build result
        r = {
            "id": self.object.id,
            "service": self.object,
            "current_duration": now - self.object.state_changed,
            "services": services,
            "interface": interface,
            "managed_object": managed_object,
            "managed_object_status": managed_obect_status,
            "alarms": alarms,
            "errors": errors,
            "warnings": warnings,
            "maintenance": maintenance,
        }
        return r

    def get_services(self):
        def get_children(ca):
            ca._children = []
            for a in Service.objects.filter(parent=ca):
                ca._children += [a]
                get_children(a)

        def flatten(ca, r, level):
            ca._level = level
            r += [ca]
            if hasattr(ca, "_children"):
                for c in sorted(ca._children, key=operator.attrgetter("ts")):
                    flatten(c, r, level + 1)

        # Step upwards
        r = self.object
        a = r
        while r and r.parent:
            a = r.parent
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

    def get_interface(self):
        svc = self.object
        while svc:
            iface = svc.interface
            if iface:
                return iface
            svc = svc.parent
        return None
