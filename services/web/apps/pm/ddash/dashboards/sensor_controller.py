# ---------------------------------------------------------------------
# Sensor Controller's dynamic dashboard
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-Party modules
from collections import defaultdict

# NOC modules
from .mo import MODashboard
from noc.inv.models.interface import Interface
from noc.pm.models.metrictype import MetricType

TITLE_BAD_CHARS = '"\\\n\r'


class SensorControllerDashboard(MODashboard):
    name = "sensor_controller"
    template = "dash_sensor_controller.j2"
    has_capability = "Sensor | Controller"

    def resolve_object_data(self, object):
        def interface_profile_has_metrics(object):
            """
            Check interface profile has metrics
            """
            ifaces = {}
            sensors = {}
            sensors_status = []
            for iface in Interface.objects.filter(managed_object=object, type="physical"):
                if iface.name in ["eth0", "st"]:
                    ifaces[iface.name] = {
                        "type": iface.profile.id,
                        "name": iface.profile.name,
                        "status": iface.status,
                        "descr": self.str_cleanup(
                            iface.description, remove_letters=TITLE_BAD_CHARS
                        ),
                    }
                else:
                    for metric in iface.profile.metrics:
                        if (
                            metric.enable_box or metric.enable_periodic
                        ) and metric.metric_type.scope.table_name == "environment":
                            if metric.metric_type.field_name == "sensor_status":
                                sensors_status.append(iface.name)
                                continue
                            if iface.name in sensors:
                                sensors[iface.name]["metrics"] += [metric.metric_type.field_name]
                            else:
                                sensors[iface.name] = {
                                    "metrics": [metric.metric_type.field_name],
                                    "profile": iface.profile.name,
                                    "status": iface.status,
                                    "descr": self.str_cleanup(
                                        iface.description, remove_letters=TITLE_BAD_CHARS
                                    ),
                                }
            return sensors_status, sensors, ifaces

        port_types = []
        sensor_types = []
        object_metrics = []
        ports = []
        selected_types = defaultdict(list)
        # Get all interface profiles with configurable metrics
        sensors_status, sensors, ifaces = interface_profile_has_metrics(self.object.id)
        # Create charts for configured interface metrics
        for sensor in sorted(sensors.keys()):
            sensor_types += [
                {
                    "name": sensor,
                    "metrics": sensors[sensor].get("metrics"),
                    "profile": sensors[sensor].get("profile"),
                    "descr": sensors[sensor].get("descr"),
                    "status": sensors[sensor].get("status"),
                }
            ]
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
                {
                    "type": ifaces[iface].get("type"),
                    "name": ifaces[iface].get("name"),
                    "ports": ports,
                }
            ]

        if self.object.object_profile.report_ping_rtt:
            object_metrics += ["rtt"]

        om = []
        for metrics in self.object.object_profile.metrics or []:
            mt = MetricType.get_by_id(metrics["metric_type"])
            if not mt:
                continue
            om += [mt.name]
        object_metrics.extend(sorted(om))

        return {
            "sensors_status": sensors_status,
            "sensor_types": sensor_types,
            "port_types": port_types,
            "selected_types": selected_types,
            "object_metrics": object_metrics,
        }

    def get_context(self):
        return {
            "port_types": self.object_data["port_types"],
            "sensor_types": self.object_data["sensor_types"],
            "sensors_status": self.object_data["sensors_status"],
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
            "selected_types": self.object_data["selected_types"],
            "ping_interval": self.object.object_profile.ping_interval,
            "discovery_interval": "%ss"
            % int(self.object.object_profile.periodic_discovery_interval / 2),
        }
