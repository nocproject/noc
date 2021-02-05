# ---------------------------------------------------------------------
# DVBC dynamic dashboard
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-Party modules
from django.db.models import Q
from collections import defaultdict

# NOC modules
from .jinja import JinjaDashboard
from noc.inv.models.interface import Interface
from noc.pm.models.metrictype import MetricType
from noc.core.validators import is_ipv4
from noc.sa.models.managedobject import ManagedObject

TITLE_BAD_CHARS = '"\\\n\r'


class DVBCDashboard(JinjaDashboard):
    name = "modvbc"
    template = "dash_modvbc.j2"

    def resolve_object(self, object):
        o = ManagedObject.objects.filter(Q(id=object) | Q(bi_id=object))[:1]
        if not o:
            raise self.NotFound()
        else:
            return o[0]

    def resolve_object_data(self, object):
        def interface_profile_has_metrics(object):
            """
            Check interface profile has metrics
            """
            ifaces = {}
            channels = []
            groups = []
            for iface in Interface.objects.filter(managed_object=object, type="physical"):
                if "gbe" in iface.name.lower():
                    ifaces[iface.name] = {
                        "type": iface.profile.id,
                        "name": iface.profile.name,
                        "status": iface.status,
                        "descr": self.str_cleanup(
                            iface.description, remove_letters=TITLE_BAD_CHARS
                        ),
                    }
                    continue
                for metric in iface.profile.metrics:
                    if metric.enable_box or metric.enable_periodic:
                        if is_ipv4(iface.name.split("/")[1]):
                            groups.append(iface.name)
                        else:
                            channels.append(iface.name)

            return ifaces, channels, groups

        port_types = []
        object_metrics = []
        ports = []
        # Get all interface profiles with configurable metrics
        ifaces, channels, groups = interface_profile_has_metrics(self.object.id)
        # Create charts for configured interface metrics
        for iface in sorted(ifaces.keys()):
            ports += [
                {
                    "name": iface,
                    "descr": ifaces[iface].get("descr"),
                    "status": ifaces[iface].get("status"),
                }
            ]
        port_types += [
            {"type": ifaces[iface].get("type"), "name": ifaces[iface].get("name"), "ports": ports}
        ]
        if self.object.object_profile.report_ping_rtt:
            object_metrics += ["rtt"]

        om = []
        for metrics in self.object.object_profile.metrics or []:
            mt = MetricType.get_by_id(metrics["metric_type"])
            if not mt or not (
                metrics.get("enable_periodic", False) or metrics.get("enable_box", False)
            ):
                continue
            om += [mt.name]
        object_metrics.extend(sorted(om))
        if self.extra_template and self.extra_vars:
            self.template = "dash_multicast.j2"
        return {
            "channels": set(channels),
            "groups": set(groups),
            "port_types": port_types,
            "object_metrics": object_metrics,
        }

    def get_context(self):

        return {
            "port_types": self.object_data["port_types"],
            "groups": self.object_data["groups"],
            "channels": self.object_data["channels"],
            "object_metrics": self.object_data["object_metrics"],
            "device": self.object.name.replace('"', ""),
            "ip": self.object.address,
            "platform": self.object.platform.name if self.object.platform else "Unknown platform",
            "device_id": self.object.id,
            "firmare_version": self.object.version.version if self.object.version else None,
            "segment": self.object.segment.id,
            "vendor": self.object.vendor or "Unknown version",
            "bi_id": self.object.bi_id,
            "pool": self.object.pool.name,
            "extra_template": self.extra_template,
            "extra_vars": self.extra_vars,
            "selected_types": defaultdict(list),
            "ping_interval": self.object.object_profile.ping_interval,
            "discovery_interval": self.object.object_profile.periodic_discovery_interval,
        }
