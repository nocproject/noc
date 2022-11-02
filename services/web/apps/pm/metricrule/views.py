# ---------------------------------------------------------------------
# pm.metricrule application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.app.extdocapplication import ExtDocApplication
from noc.pm.models.metricrule import MetricRule
from noc.core.translation import ugettext as _


class MetricRuleApplication(ExtDocApplication):
    """
    MetricType application
    """

    title = _("Metric Rule")
    menu = [_("Setup"), _("Metric Rules")]
    model = MetricRule
    query_condition = "icontains"
    query_fields = ["name", "description"]

    def instance_to_dict(self, o: "MetricRule", fields=None, nocustom=False):
        r = super().instance_to_dict(o, fields=fields, nocustom=nocustom)
        if r.get("actions") and (not fields or "actions" in fields):
            for action, edoc in zip(o.actions, r["actions"]):
                edoc["metric_action_params"] = self.params_to_list(
                    action, edoc.get("metric_action_params")
                )
        return r

    @staticmethod
    def params_to_list(action, params):
        params = params or {}
        r = []
        for p in action.metric_action.params:
            r += [
                {
                    "name": p.name,
                    "type": p.type,
                    "value": params.get(p.name) or "",
                    "default": p.default,
                    "description": p.description,
                }
            ]
        return r

    @staticmethod
    def list_to_params(params):
        return {p["name"]: p["value"] for p in params if p.get("value")}

    def clean(self, data):
        for rule in data.get("actions", []):
            rule["metric_action_params"] = self.list_to_params(
                rule.get("metric_action_params") or []
            )
        return super().clean(data)
