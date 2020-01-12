# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ManagedObject's dynamic dashboard
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import

# Third-Party modules
import demjson
from django.db.models import Q
from jinja2 import Environment, FileSystemLoader

# NOC modules
from .base import BaseDashboard
from noc.config import config
from noc.inv.models.interface import Interface
from noc.inv.models.subinterface import SubInterface
from noc.core.text import alnum_key
from noc.pm.models.metrictype import MetricType
from noc.sa.models.managedobject import ManagedObject

TITLE_BAD_CHARS = '"\\\n\r'


class MODashboard(BaseDashboard):
    name = "mo"

    def resolve_object(self, object):
        o = ManagedObject.objects.filter(Q(id=object) | Q(bi_id=object))[:1]
        if not o:
            raise self.NotFound()
        else:
            return o[0]

    def resolve_object_data(self, object):
        def interface_profile_has_metrics(profile):
            """
            Check interface profile has metrics
            """
            for m in profile.metrics:
                if m.enable_box or m.enable_periodic:
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

        def check_metrics(metric):
            """
            Object check metrics
            """
            if metric.name.startswith("Check"):
                return True
            return False

        port_types = []
        object_metrics = []
        object_check_metrics = []
        lags = []
        subif = []
        radio_types = []

        # Get all interface profiles with configurable metrics
        all_ifaces = list(Interface.objects.filter(managed_object=self.object.id))
        iprof = set(i.profile for i in all_ifaces)
        # @todo: Order by priority
        profiles = [p for p in iprof if interface_profile_has_metrics(p)]
        # Create charts for configured interface metrics
        for profile in profiles:
            ifaces = [i for i in all_ifaces if i.profile == profile]
            ports = []
            radio = []
            for iface in sorted(ifaces, key=lambda el: alnum_key(el.name)):
                if iface.type == "SVI" and not iface.profile.allow_subinterface_metrics:
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
                if interface_radio_metrics(profile):
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
                if iface.type == "physical":
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
            if ports:
                port_types += [{"type": profile.id, "name": profile.name, "ports": ports}]
            if radio:
                radio_types += [{"type": profile.id, "name": profile.name, "ports": radio}]

        if self.object.object_profile.report_ping_rtt:
            object_metrics += ["rtt"]

        om = []
        ocm = []
        for m in self.object.object_profile.metrics or []:
            mt = MetricType.get_by_id(m["metric_type"])
            if not mt or not (m.get("enable_periodic", False) or m.get("enable_box", False)):
                continue
            if check_metrics(mt):
                ocm += [{"name": mt.name, "metric": mt.field_name}]
                continue
            om += [mt.name]
        object_metrics.extend(sorted(om))
        object_check_metrics.extend(sorted(ocm))

        return {
            "port_types": port_types,
            "object_metrics": object_metrics,
            "object_check_metrics": object_check_metrics,
            "lags": lags,
            "subifaces": subif,
            "radio_types": radio_types,
        }

    def render(self):

        context = {
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
            "bi_id": self.object.bi_id,
            "pool": self.object.pool.name,
            "extra_template": self.extra_template,
            "ping_interval": self.object.object_profile.ping_interval,
            "discovery_interval": self.object.object_profile.periodic_discovery_interval,
        }
        self.logger.info("Context with data: %s" % context)
        j2_env = Environment(loader=FileSystemLoader(config.path.pm_templates))
        tmpl = j2_env.get_template("dash_mo.j2")
        data = tmpl.render(context)
        render = demjson.decode(data)
        return render
