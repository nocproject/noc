# ---------------------------------------------------------------------
# ManagedObject's dynamic dashboard
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-Party modules
import demjson
import json
from django.db.models import Q
from jinja2 import Environment, FileSystemLoader

# NOC modules
from .base import BaseDashboard
from noc.config import config
from noc.inv.models.interface import Interface
from noc.inv.models.subinterface import SubInterface
from noc.sa.models.managedobject import ManagedObject

TITLE_BAD_CHARS = '"\\\n\r'


class MOCardDashboard(BaseDashboard):
    name = "mocard"

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

        object_metrics = []
        port_types = []
        subif = []
        radio_types = []
        extra_template = self.extra_template.replace("'", '"')
        result = json.loads(extra_template)
        if result["type"] == "iface":
            radio = []
            iface = Interface.objects.get(managed_object=self.object.id, name=result["name"])
            iprof = iface.profile if interface_profile_has_metrics(iface.profile) else None
            if iprof:
                metrics = [str(m.metric_type.field_name) for m in iface.profile.metrics]
                if interface_radio_metrics(iface.profile):
                    radio = {
                        "name": iface.name,
                        "descr": self.str_cleanup(
                            iface.description, remove_letters=TITLE_BAD_CHARS
                        ),
                        "status": iface.status,
                        "metrics": interface_radio_metrics(iface.profile),
                    }
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
                if iface.type == "physical":
                    port = {
                        "name": iface.name,
                        "descr": self.str_cleanup(
                            iface.description, remove_letters=TITLE_BAD_CHARS
                        ),
                        "status": iface.status,
                    }
                if port:
                    port_types = {"name": iface.profile.name, "port": port, "metrics": metrics}
                if radio:
                    radio_types = {"name": iface.profile.name, "port": radio, "metrics": metrics}

            return {
                "object_metrics": object_metrics,
                "port_types": port_types,
                "subifaces": subif,
                "radio_types": radio_types,
            }

    def render(self):

        context = {
            "port_types": self.object_data["port_types"],
            "object_metrics": self.object_data["object_metrics"],
            "device": self.object.name.replace('"', ""),
            "subifaces": self.object_data["subifaces"],
            "radio_types": self.object_data["radio_types"],
            "bi_id": self.object.bi_id,
            "pool": self.object.pool.name,
            "ping_interval": self.object.object_profile.ping_interval,
            "discovery_interval": self.object.object_profile.periodic_discovery_interval,
        }
        self.logger.info("Context with data: %s" % context)
        j2_env = Environment(loader=FileSystemLoader(config.path.pm_templates))
        tmpl = j2_env.get_template("dash_mo_card.j2")
        data = tmpl.render(context)
        render = demjson.decode(data)
        return render
