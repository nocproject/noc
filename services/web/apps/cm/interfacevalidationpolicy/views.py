# ----------------------------------------------------------------------
# cm.interfacevalidationpolicy application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.cm.models.interfacevalidationpolicy import InterfaceValidationPolicy
from noc.core.translation import ugettext as _


class InterfaceValidationPolicyApplication(ExtDocApplication):
    """
    InterfaceValidationPolicy application
    """

    title = "Interface Validation Policy"
    menu = [_("Setup"), _("Interface Validation Policies")]
    model = InterfaceValidationPolicy
    glyph = "ambulance"
    implied_permissions = {
        "create": ["cm:confdbquery:lookup", "cm:confdbquery:read"],
        "update": ["cm:confdbquery:lookup", "cm:confdbquery:read"],
    }

    def instance_to_dict(self, o, fields=None, nocustom=False):
        v = super().instance_to_dict(o, fields=fields, nocustom=nocustom)
        if v.get("rules") and (not fields or "rules" in fields):
            for rule, edoc in zip(o.rules, v["rules"]):
                edoc["query_params"] = self.params_to_list(rule, edoc.get("query_params"))
        return v

    @staticmethod
    def params_to_list(rule, params):
        params = params or {}
        r = []
        for p in rule.query.params:
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
        return {p["name"]: p["value"] for p in params if p["value"] != ""}

    def clean(self, data):
        for rule in data.get("rules", []):
            rule["query_params"] = self.list_to_params(rule.get("query_params") or [])
        return super().clean(data)
