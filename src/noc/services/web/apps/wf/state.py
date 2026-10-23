# ----------------------------------------------------------------------
# wf.state application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.wf.models.workflow import Workflow
from noc.wf.models.state import State, InteractionSetting
from noc.core.translation import ugettext as _


class StateApplication(ExtDocApplication):
    """
    State application
    """

    title = _("States")
    menu = [_("Setup"), _("States")]
    query_condition = "icontains"
    model = State

    def cleaned_query(self, q):
        if "id__referred" in q:
            m1, m2 = q["id__referred"].split("__")[0].split(".")
            q["workflow__in"] = list(
                Workflow.objects.filter(allowed_models=f"{m1}.{m2.capitalize()}").values_list("id")
            )
            q.pop("id__referred")
        elif "allowed_models" in q:
            q["workflow__in"] = list(
                Workflow.objects.filter(allowed_models=q["allowed_models"]).values_list("id")
            )
            q.pop("allowed_models")
        return super().cleaned_query(q)

    def instance_to_dict(self, o, fields=None, nocustom=False):
        r = super().instance_to_dict(o, fields)
        if "interaction_settings" in r:
            r["interaction_settings"] = [
                {"interaction": f, "enable": r["interaction_settings"][f].enable}
                for f in r["interaction_settings"]
            ]
        return r

    def clean(self, data):
        interaction_settings = {}
        for f in data.get("interaction_settings", []):
            interaction_settings[f["interaction"]] = InteractionSetting(**{"enable": f["enable"]})
        data["interaction_settings"] = interaction_settings
        return super().clean(data)
