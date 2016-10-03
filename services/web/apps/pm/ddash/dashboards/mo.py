# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ManagedObject's dynamic dashboard
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

import os
## NOC modules
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
            for iface in sorted(ifaces, key=split_alnum):
                ports += [{"name": iface.name, "descr": iface.description}]
                if iface.is_linked:
                    ports[-1]["link_id"] = str(iface.link.id)

            port_types += [{"type": profile.name,  "name": profile.name,
                            "ports": ports}]

        transform = {"CPU | Usage": "cpu",
                     "Ping | RTT": "rtt",
                     "Memory | Usage": "memory",
                     "Radio | CINR": "cinr",
                     "Radio | RSSI": "rssi"
                    }
        if self.object.object_profile.report_ping_rtt:
            object_metrics += ["rtt"]
        for m in (self.object.object_profile.metrics or []):
            mt = MetricType.get_by_id(m["metric_type"])
            if not mt or not m.get("is_active", False):
                continue
            object_metrics += [transform[mt.name]]

        return {"port_types": port_types,
                "object_metrics": object_metrics}

    def render(self):

        context = {
            "port_types": self.object_data["port_types"],
            "object_metrics": self.object_data["object_metrics"],
            "device": self.object.name,
            "ip": self.object.address,
            "platform": self.object.platform or "Unknown platform",
            "device_id": self.object.id,
            "vendor": self.object.vendor or "Unknown platform"
        }
        self.logger.info("Context with data: %s" % context)
        PM_TEMPLATE_PATH = "templates/ddash/"
        j2_env = Environment(loader=FileSystemLoader(PM_TEMPLATE_PATH))
        tmpl = j2_env.get_template("dash_mo.j2")
        # with open(MO_TEMPLATE_PATH) as f:
        #    CARD_TEMPLATE = Template(f.read())
        return json.loads(tmpl.render(context))
