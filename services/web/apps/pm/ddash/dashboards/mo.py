# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ManagedObject's dynamic dashboard
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

import demjson
from django.db.models import Q
from jinja2 import Environment, FileSystemLoader
from noc.config import config
from noc.inv.models.interface import Interface
from noc.inv.models.subinterface import SubInterface
# NOC modules
from noc.lib.text import split_alnum
from noc.pm.models.metrictype import MetricType
from noc.sa.models.managedobject import ManagedObject

from base import BaseDashboard


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

        port_types = []
        object_metrics = []
        lags = []
        subif = []

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
                if iface.type == 'SVI' and not iface.profile.allow_subinterface_metrics:
                    continue
                if iface.type == u"aggregated" and iface.lag_members:
                    lags += [{
                        "name": iface.name,
                        "ports": [i.name for i in iface.lag_members],
                        "descr": self.str_cleanup(iface.description) or "No description",
                        "status": ["status : ".join([i.name, i.status]) for i in iface.lag_members]
                    }]
                    continue
                ports += [{"name": iface.name, "descr": self.str_cleanup(iface.description), "status": iface.status}]
                if iface.profile.allow_subinterface_metrics:
                    subif += [{
                        "name": si.name,
                        "descr": self.str_cleanup(si.description)
                    } for si in SubInterface.objects.filter(interface=iface)]
            if not ports:
                continue
            port_types += [{"type": profile.id, "name": profile.name,
                            "ports": ports}]

        if self.object.object_profile.report_ping_rtt:
            object_metrics += ["rtt"]
        om = []
        for m in (self.object.object_profile.metrics or []):
            mt = MetricType.get_by_id(m["metric_type"])
            if not mt or not (m.get("enable_periodic", False) or m.get("enable_box", False)):
                continue
            om += [mt.name]
        object_metrics.extend(sorted(om))

        return {"port_types": port_types,
                "object_metrics": object_metrics,
                "lags": lags,
                "subifaces": subif}

    def render(self):

        context = {
            "port_types": self.object_data["port_types"],
            "object_metrics": self.object_data["object_metrics"],
            "lags": self.object_data["lags"],
            "device": self.object.name.replace('\"', ''),
            "ip": self.object.address,
            "platform": self.object.platform.name if self.object.platform else "Unknown platform",
            "device_id": self.object.id,
            "firmare_version": self.object.version.version if self.object.version else None,
            "segment": self.object.segment.id,
            "vendor": self.object.vendor or "Unknown version",
            "subifaces": self.object_data["subifaces"],
            "bi_id": self.object.bi_id,
            "pool": self.object.pool.name,
            "ping_interval": self.object.object_profile.ping_interval,
            "discovery_interval": self.object.object_profile.periodic_discovery_interval
        }
        self.logger.info("Context with data: %s" % context)
        j2_env = Environment(loader=FileSystemLoader(config.path.pm_templates))
        tmpl = j2_env.get_template("dash_mo.j2")
        data = tmpl.render(context)

        render = demjson.decode(data)
        return render
