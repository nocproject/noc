# ----------------------------------------------------------------------
# wf.state application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.wf.models.workflow import Workflow
from noc.wf.models.state import State, FeatureSetting
from noc.core.translation import ugettext as _


class StateApplication(ExtDocApplication):
    """
    State application
    """

    title = _("States")
    menu = [_("Setup"), _("States")]
    model = State

    def cleaned_query(self, q):
        if "id__referred" in q:
            m1, m2 = q["id__referred"].split("__")[0].split(".")
            q["workflow__in"] = list(
                Workflow.objects.filter(allowed_models=f"{m1}.{m2.capitalize()}").values_list("id")
            )
            q.pop("id__referred")
        return super().cleaned_query(q)

    def instance_to_dict(self, o, fields=None, nocustom=False):
        r = super().instance_to_dict(o, fields)
        if "feature_settings" in r:
            r["feature_settings"] = [
                {"feature": f, "enable": r["feature_settings"][f].enable}
                for f in r["feature_settings"]
            ]
        return r

    def clean(self, data):
        feature_settings = {}
        for f in data.get("feature_settings", []):
            feature_settings[f["feature"]] = FeatureSetting(**{"enable": f["enable"]})
        data["feature_settings"] = feature_settings
        return super().clean(data)
