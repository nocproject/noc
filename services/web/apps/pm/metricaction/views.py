# ---------------------------------------------------------------------
# pm.metricrule application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication
from noc.pm.models.metricaction import MetricAction
from noc.fm.models.alarmclass import AlarmClass
from noc.core.translation import ugettext as _


class MetricActionApplication(ExtDocApplication):
    """
    MetricType application
    """

    title = _("Metric Action")
    menu = [_("Setup"), _("Metric Actions")]
    model = MetricAction
    query_condition = "icontains"
    query_fields = ["name", "description"]

    def instance_to_dict(self, o, fields=None, nocustom=False):
        v = super().instance_to_dict(o, fields=fields, nocustom=nocustom)
        if "activation_config" in v:
            r = {}
            if v["alarm_node"]:
                r["alarm_node"] = v["alarm_node"]
                if v["alarm_config"]["alarm_class"]:
                    r["alarm_class"] = str(
                        AlarmClass.get_by_name(v["alarm_config"]["alarm_class"]).id
                    )
                    r["alarm_class__label"] = str(
                        AlarmClass.get_by_name(v["alarm_config"]["alarm_class"]).name
                    )
                r["activation_level"] = v["alarm_config"].get("activation_level")
            if v["compose_node"]:
                r["compose_node"] = v["compose_node"]
                r["compose_inputs"] = v["compose_inputs"]
                r["compose_metric_type"] = v["compose_metric_type"]
            if v["activation_node"]:
                r["activation_node"] = v["activation_node"]
                r["activation_config"] = [
                    {"param": k, "value": v} for k, v in v["activation_config"].items()
                ]
            if r:
                return r
        return v

    @staticmethod
    def list_to_params(params):
        return {p["name"]: p["value"] for p in params if p["value"] != ""}

    def clean(self, data):
        actions = []
        for a in data["actions"]:
            r = {}
            if a["alarm_node"]:
                r["alarm_node"] = a["alarm_node"]
                r["alarm_config"] = {
                    "alarm_class": AlarmClass.get_by_id(a["alarm_class"]).name,
                    "activation_level": float(a.get("activation_level", 1.0)),
                }
            if a["compose_node"]:
                r["compose_node"] = a["compose_node"]
                r["compose_inputs"] = a["compose_inputs"]
                r["compose_metric_type"] = a["compose_metric_type"]
            if a["activation_node"]:
                r["activation_node"] = a["activation_node"]
                r["activation_config"] = self.list_to_params(a["activation_config"])
            if r:
                actions += [r]
        data["actions"] = actions
        return super().clean(data)
