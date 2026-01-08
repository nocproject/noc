# ---------------------------------------------------------------------
# ManagedObject's dynamic dashboard
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-Party modules
import operator
from django.db.models import Q
from collections import defaultdict
from mongoengine.queryset.visitor import Q as m_q


# NOC modules
from .jinja import JinjaDashboard
from noc.inv.models.interface import Interface
from noc.inv.models.subinterface import SubInterface
from noc.inv.models.object import Object
from noc.inv.models.sensor import Sensor
from noc.core.text import alnum_key
from noc.pm.models.metrictype import MetricType
from noc.sa.models.managedobject import ManagedObject

TITLE_BAD_CHARS = '"\\\n\r'


class MODashboard(JinjaDashboard):
    name = "mo"
    template = "dash_mo.j2"
    has_capability = None

    def __new__(cls, *args, **kwargs):
        from .loader import loader

        object_id, *_ = args
        mo: ManagedObject = cls.resolve_object(object_id)
        caps = mo.get_caps()
        dash = cls
        for capability in loader.caps_map:
            if capability in caps:
                dash = loader.caps_map[capability]
        return super().__new__(dash)

    @classmethod
    def resolve_object(cls, object_id) -> "ManagedObject":
        o = ManagedObject.objects.filter(Q(id=object_id) | Q(bi_id=object_id)).first()
        if not o:
            raise cls.NotFound()
        return o

    def resolve_object_data(self, object):
        def interface_profile_has_metrics(profile):
            """
            Check interface profile has metrics
            """
            for m in profile.metrics:
                if (
                    m.interval
                    or profile.metrics_default_interval
                    or self.object.object_profile.metrics_default_interval
                ):
                    return True
            return False

        def interface_radio_metrics(profile):
            """
            Check interface profile has metrics
            """
            metrics = []
            for m in profile.metrics:
                if m.metric_type.name.startswith("Radio"):
                    metrics.append(m.metric_type.field_name)
            if metrics:
                return metrics
            return None

        def interface_dom_metrics(profile):
            """
            Check interface profile has metrics
            """
            metrics = []
            for m in profile.metrics:
                if m.metric_type.name.startswith("Interface | DOM"):
                    metrics.append(m.metric_type.field_name)
            if metrics:
                return metrics
            return None

        def check_metrics(metric):
            """
            Object check metrics
            """
            return bool(metric.name.startswith("Check"))

        port_types = []
        object_metrics = []
        object_check_metrics = []
        lags = []
        subif = []
        radio_types = []
        dom_types = []
        selected_types = defaultdict(list)
        selected_ifaces = set(self.extra_vars.get("var_ifaces", "").split(","))
        # Get all interface profiles with configurable metrics
        all_ifaces = list(Interface.objects.filter(managed_object=self.object.id))
        iprof = {i.profile for i in all_ifaces}
        # @todo: Order by priority
        profiles = [p for p in iprof if interface_profile_has_metrics(p)]
        # Create charts for configured interface metrics
        for profile in profiles:
            ifaces = [i for i in all_ifaces if i.profile == profile]
            ports = []
            radio = []
            dom = []
            for iface in sorted(ifaces, key=lambda el: alnum_key(el.name)):
                if iface.type == "SVI" and (iface.profile.is_default or not iface.profile.metrics):
                    continue
                if iface.type == "aggregated" and iface.lag_members:
                    lags += [
                        {
                            "name": iface.name,
                            "ports": [i.name for i in iface.lag_members],
                            "descr": self.str_cleanup(
                                iface.description, remove_letters=TITLE_BAD_CHARS
                            )
                            or "No description",
                            "status": [
                                ", Status : ".join([i.name, i.status]) for i in iface.lag_members
                            ],
                        }
                    ]
                    continue
                if "technology::radio::*" in iface.effective_labels:
                    radio += [
                        {
                            "name": iface.name,
                            "descr": self.str_cleanup(
                                iface.description, remove_letters=TITLE_BAD_CHARS
                            ),
                            "status": iface.status,
                            "metrics": interface_radio_metrics(profile),
                        }
                    ]
                if interface_dom_metrics(profile) and iface.type == "physical":
                    dom += [
                        {
                            "name": iface.name,
                            "descr": self.str_cleanup(
                                iface.description, remove_letters=TITLE_BAD_CHARS
                            ),
                            "status": iface.status,
                            "metrics": interface_dom_metrics(profile),
                            "type": profile.id,
                            "profile_name": profile.name,
                        }
                    ]
                if iface.type == "SVI":
                    ports += [
                        {
                            "name": iface.name,
                            "descr": self.str_cleanup(
                                iface.description, remove_letters=TITLE_BAD_CHARS
                            ),
                            "status": iface.status,
                        }
                    ]
                if iface.type in ("physical", "tunnel"):
                    ports += [
                        {
                            "name": iface.name,
                            "descr": self.str_cleanup(
                                iface.description, remove_letters=TITLE_BAD_CHARS
                            ),
                            "status": iface.status,
                        }
                    ]
                if iface.profile.allow_subinterface_metrics:
                    subif += [
                        {
                            "name": si.name,
                            "descr": self.str_cleanup(
                                si.description, remove_letters=TITLE_BAD_CHARS
                            ),
                        }
                        for si in SubInterface.objects.filter(interface=iface)
                    ]
                if iface.name in selected_ifaces:
                    selected_types[profile.id] += [iface.name]
            if ports:
                port_types += [{"type": profile.id, "name": profile.name, "ports": ports}]
            if radio:
                radio_types += [{"type": profile.id, "name": profile.name, "ports": radio}]
            if dom:
                dom_types += dom

        if self.object.object_profile.report_ping_rtt:
            object_metrics += ["rtt"]

        om = []
        ocm = []
        for m in self.object.object_profile.metrics or []:
            mt = MetricType.get_by_id(m["metric_type"])
            if not mt:
                continue
            if check_metrics(mt):
                ocm += [{"name": mt.name, "metric": mt.field_name}]
                continue
            om += [mt.name]

        object_metrics.extend(sorted(om))
        object_check_metrics.extend(sorted(ocm, key=operator.itemgetter("name")))
        # Sensors
        sensor_types = defaultdict(list)
        sensor_enum = []
        o = Object.get_managed(self.object.id) or []
        for s in Sensor.objects.filter(m_q(managed_object=self.object) | m_q(object__in=o)):
            s_type = s.profile.name
            if not s.state.is_productive:
                s_type = "missed"
            if s.munits.enum and s.state.is_productive:
                sensor_enum += [{"bi_id": s.bi_id, "local_id": s.local_id, "units": s.munits}]
            sensor_types[s_type] += [
                {
                    "label": s.dashboard_label or s.label,
                    "units": s.munits,
                    "bi_id": s.bi_id,
                    "local_id": s.local_id,
                    "profile": s.profile,
                    "id": int(str(s.bi_id)[-10:]),
                }
            ]

        return {
            "port_types": port_types,
            "selected_types": selected_types,
            "object_metrics": object_metrics,
            "object_check_metrics": object_check_metrics,
            "lags": lags,
            "subifaces": subif,
            "sensor_enum": sensor_enum,
            "sensor_types": sensor_types,
            "radio_types": radio_types,
            "dom_types": sorted(dom_types, key=lambda x: alnum_key(x["name"])),
        }

    def get_context(self):
        return {
            "port_types": self.object_data["port_types"],
            "object_metrics": self.object_data["object_metrics"],
            "object_check_metrics": self.object_data["object_check_metrics"],
            "lags": self.object_data["lags"],
            "device": self.object.name.replace('"', ""),
            "ip": self.object.address,
            "platform": self.object.platform.name if self.object.platform else "Unknown platform",
            "device_id": self.object.id,
            "firmare_version": self.object.version.version if self.object.version else None,
            "segment": self.object.segment.id,
            "vendor": self.object.vendor or "Unknown version",
            "subifaces": self.object_data["subifaces"],
            "radio_types": self.object_data["radio_types"],
            "dom_types": self.object_data["dom_types"],
            "sensor_types": self.object_data["sensor_types"],
            "sensor_enum": self.object_data["sensor_enum"],
            "bi_id": self.object.bi_id,
            "pool": self.object.pool.name,
            "extra_template": self.extra_template,
            "extra_vars": self.extra_vars,
            "selected_types": self.object_data["selected_types"],
            "ping_interval": self.object.object_profile.ping_interval,
            "discovery_interval": int(self.object.get_metric_discovery_interval() / 2),
        }
