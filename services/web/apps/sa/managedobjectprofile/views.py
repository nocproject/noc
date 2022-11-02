# ---------------------------------------------------------------------
# sa.managedobjectprofile application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.app.extmodelapplication import ExtModelApplication
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.core.translation import ugettext as _
from noc.pm.models.metrictype import MetricType
from noc.pm.models.thresholdprofile import ThresholdProfile


class ManagedObjectProfileApplication(ExtModelApplication):
    """
    ManagedObjectProfile application
    """

    title = _("Managed Object Profile")
    menu = [_("Setup"), _("Managed Object Profiles")]
    model = ManagedObjectProfile
    query_condition = "icontains"
    query_fields = ["name", "description"]

    implied_permissions = {"launch": ["ip:addressprofile:lookup"]}

    def field_row_class(self, o):
        return o.style.css_class_name if o.style else ""

    def field_mo_count(self, o):
        return o.managedobject_set.count()

    def instance_to_dict(self, o, fields=None):
        d = super().instance_to_dict(o, fields=fields)
        if d["metrics"]:
            for m in d["metrics"]:
                mt = MetricType.get_by_id(m["metric_type"])
                if mt:
                    m["metric_type__label"] = mt.name
                if m.get("threshold_profile"):
                    tp = ThresholdProfile.get_by_id(m["threshold_profile"])
                    m["threshold_profile__label"] = tp.name
        return d
