# ---------------------------------------------------------------------
# inv.objectconfigurationrule application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.inv.models.objectconfigurationrule import ObjectConfigurationRule, ConnectionRule
from noc.core.translation import ugettext as _


class ObjectConfigurationRuleApplication(ExtDocApplication):
    """
    Configuration Rule application
    """

    title = _("Configuration Rules")
    menu = [_("Setup"), _("Configuration Rules")]
    model = ObjectConfigurationRule
    query_fields = ["name__icontains"]

    def instance_to_dict(self, o, fields=None, nocustom=False):
        if isinstance(o, ConnectionRule):
            r = {
                "scope": str(o.scope.id),
                "scope__label": o.scope.name,
                "match_context": o.match_context,
                "match_connection_type": None,
                "match_protocols": [
                    {"id": str(p.id), "label": p.code} for p in o.match_protocols or []
                ],
                "allowed_params": [
                    {"id": str(p.id), "label": p.code} for p in o.allowed_params or []
                ],
                "deny_params": [{"id": str(p.id), "label": p.code} for p in o.deny_params or []],
            }
            if o.match_connection_type:
                r["match_connection_type"] = str(o.match_connection_type.id)
                r["match_connection_type__label"] = o.match_connection_type.name
            return r
        return super().instance_to_dict(o, fields, nocustom=nocustom)

    def clean(self, data):
        for r in data["param_rules"]:
            if "choices" in r and isinstance(r["choices"], str):
                r["choices"] = [x.strip() for x in r["choices"].split(",") if x.strip()]
            if "dependency_param_values" in r and isinstance(r["dependency_param_values"], str):
                r["dependency_param_values"] = [
                    x.strip() for x in r["dependency_param_values"].split(",") if x.strip()
                ]
        return super().clean(data)
