# ---------------------------------------------------------------------
# fm.dispositionrule application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.fm.models.dispositionrule import DispositionRule
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
            if r["interaction_audit"] == 0:
                r["interaction_audit"] = 99
        elif isinstance(o, DispositionRule) and not o.object_actions:
            r |= {"run_discovery": False, "interaction_audit": None}
        return r

    def clean(self, data):
        rd, ia = data.pop("run_discovery", None), data.pop("interaction_audit", None)
        # ExtJS set zero value to default ComboBox
        if ia == 99:
            ia = 0
        if not rd and ia is not None:
            data.pop("object_actions", None)
        else:
            data["object_actions"] = {"run_discovery": bool(rd), "interaction_audit": ia}
        return super().clean(data)
