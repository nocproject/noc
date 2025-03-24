# ---------------------------------------------------------------------
# fm.dispositionrule application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.fm.models.dispositionrule import DispositionRule, ObjectActionItem
from noc.core.translation import ugettext as _


class DispositionRuleApplication(ExtDocApplication):
    """
    DispositionRule application
    """

    title = _("Disposition Rule")
    menu = [_("Setup"), _("Disposition Rules")]
    model = DispositionRule
    parent_field = "replace_rule"
    query_condition = "icontains"

    def instance_to_dict(self, o, fields=None, nocustom=False):
        r = super().instance_to_dict(o, fields=fields, nocustom=nocustom)
        if isinstance(o, DispositionRule) and o.object_actions:
            oa = r.pop("object_actions")
            r |= oa
        return r

    def clean(self, data):
        data["object_actions"] = {
            "run_discovery": bool(data.pop("run_discovery", None)),
            "interaction_audit": data.pop("interaction_audit", None),
        }
        return super().clean(data)
