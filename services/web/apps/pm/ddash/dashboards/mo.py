# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ManagedObject's dynamic dashboard
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

import os
# NOC modules
from noc.lib.text import split_alnum
from noc.sa.models.managedobject import ManagedObject
from base import BaseDashboard
from noc.inv.models.interface import Interface
from noc.pm.models.metrictype import MetricType
from jinja2 import Environment, FileSystemLoader
import json


class MODashboard(BaseDashboard):
    name = "mo"

    def resolve_object(self, object):
        try:
            return ManagedObject.objects.get(id=object)
        except ManagedObject.DoesNotExist:
            raise self.NotFound()

    def resolve_object_data(self, object):
        def interface_profile_has_metrics(profile):
            """
            Check interface profile has metrics
            """
            for m in profile.metrics:
                if m.is_active:
                    return True
            return False

        port_types = []
        object_metrics = []
        lags = []

        # Get all interface profiles with configurable metrics
        all_ifaces = list(Interface.objects.filter(
            managed_object=self.object.id
        ))
        iprof = set(i.profile for i in all_ifaces)
        # @todo: Order by priority
        profiles = [p for p in iprof if interface_profile_has_metrics(p)]
        # Create charts for configured interface metrics
        for profile in profiles:
            ifaces = [i for i in all_ifaces if i.profile == profile]
            ports = []
            for iface in sorted(ifaces, key=lambda el: split_alnum(el.name)):
                if iface.description:
                    iface.description = iface.description.replace('\"', '')
                if iface.type == u"aggregated" and iface.lag_members:
                    lags += [{
                        "name": iface.name,
                        "ports": [i.name for i in iface.lag_members],
                        "descr": iface.description or "No description",
                        "status": ["status : ".join([i.name, i.status]) for i in iface.lag_members]
                    }]
                    continue
                ports += [{"name": iface.name, "descr": iface.description, "status": iface.status}]
            if not ports:
                continue
            port_types += [{"type": profile.id, "name": profile.name,
                            "ports": ports}]

        if self.object.object_profile.report_ping_rtt:
            object_metrics += ["rtt"]
        for m in (self.object.object_profile.metrics or []):
            mt = MetricType.get_by_id(m["metric_type"])
            if not mt or not m.get("is_active", False):
                continue
            object_metrics += [mt.name]

        return {"port_types": port_types,
                "object_metrics": object_metrics,
                "lags": lags}

    def render(self):

        context = {
            "port_types": self.object_data["port_types"],
            "object_metrics": self.object_data["object_metrics"],
            "lags": self.object_data["lags"],
            "device": self.object.name.replace('\"', ''),
            "ip": self.object.address,
            "platform": self.object.version.platform or "Unknown platform",
            "device_id": self.object.id,
            "firmare_version": self.object.version.version or None,
            "segment": self.object.segment.id,
            "vendor": self.object.vendor or "Unknown version",
            "bi_id": self.object.get_bi_id(),
            "pool": self.object.pool.name,
            "ping_interval": self.object.object_profile.ping_interval,
            "discovery_interval": self.object.object_profile.periodic_discovery_interval
        }
        self.logger.info("Context with data: %s" % context)
        PM_TEMPLATE_PATH = "templates/ddash/"
        j2_env = Environment(loader=FileSystemLoader(PM_TEMPLATE_PATH))
        tmpl = j2_env.get_template("dash_mo.j2")
        data = tmpl.render(context)

        render = json.loads(data)
        return render
