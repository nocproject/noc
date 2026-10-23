# ---------------------------------------------------------------------
# sa.managedobjectprofile application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extmodelapplication import ExtModelApplication
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.core.translation import ugettext as _
from noc.pm.models.metrictype import MetricType


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

    def field_mo_count(self, o):
        return o.managedobject_set.count()

    def instance_to_dict(self, o, fields=None):
        d = super().instance_to_dict(o, fields=fields)
        if d["metrics"]:
            for m in d["metrics"]:
                mt = MetricType.get_by_id(m["metric_type"])
                if mt:
                    m["metric_type__label"] = mt.name
        return d
