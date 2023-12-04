# ---------------------------------------------------------------------
# ManagedObject's dynamic dashboard
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-Party modules
import json

# NOC modules
from .mo import MODashboard
from noc.inv.models.object import Object
from noc.inv.models.interface import Interface
from noc.inv.models.subinterface import SubInterface

TITLE_BAD_CHARS = '"\\\n\r'


class MOCardDashboard(MODashboard):
    name = "mocard"
    template = "dash_mo_card.j2"

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
                if "Interface | DOM |" in m.metric_type.name:
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
        sfp_types = []
        data = None
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

        if result["type"] == "sfp":
            data = result["data"]
            sfp = []
            iface = Interface.objects.get(managed_object=self.object.id, name=result["name"])
            iprof = iface.profile if interface_profile_has_metrics(iface.profile) else None
            if iprof:
                metrics = [str(m.metric_type.field_name) for m in iface.profile.metrics]
                if interface_dom_metrics(iface.profile):
                    sfp = {
                        "name": iface.name,
                        "descr": self.str_cleanup(
                            iface.description, remove_letters=TITLE_BAD_CHARS
                        ),
                        "status": iface.status,
                        "metrics": interface_dom_metrics(iface.profile),
                    }
                if sfp:
                    sfp_types = {"name": iface.profile.name, "port": sfp, "metrics": metrics}
            o = Object.get_by_id(data["id"])
            if o:
                distance = o.get_data("optical", "distance_max") or o.model.get_data(
                    "optical", "distance_max"
                )
                data["distance"] = f"{float(distance/1000)}km" if distance else None
                data["vendor"] = o.model.vendor.name
                data["part_n"] = o.get_data(
                    "asset", "part_no", scope="discovery"
                ) or o.model.get_data("asset", "part_no")
                for c in o.model.connections:
                    if c.direction == "s" and c.name.lower() == "rx":
                        data["rx"] = ", ".join(str(p) for p in c.protocols)
                    if c.direction == "s" and c.name.lower() == "tx":
                        data["tx"] = ", ".join(str(p) for p in c.protocols)

        return {
            "object_metrics": object_metrics,
            "port_types": port_types,
            "subifaces": subif,
            "radio_types": radio_types,
            "sfp_types": sfp_types,
            "extra_vars": data,
        }

    def get_context(self):
        return {
            "port_types": self.object_data["port_types"],
            "object_metrics": self.object_data["object_metrics"],
            "device": self.object.name.replace('"', ""),
            "subifaces": self.object_data["subifaces"],
            "radio_types": self.object_data["radio_types"],
            "sfp_types": self.object_data["sfp_types"],
            "extra_vars": self.object_data["extra_vars"],
            "bi_id": self.object.bi_id,
            "pool": self.object.pool.name,
            "ping_interval": self.object.object_profile.ping_interval,
            "discovery_interval": int(self.object.object_profile.periodic_discovery_interval / 2),
        }
