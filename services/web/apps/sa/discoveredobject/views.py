# ---------------------------------------------------------------------
# sa.discoveredobject application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.services.web.base.decorators.state import state_handler
from noc.sa.models.discoveredobject import DiscoveredObject, CheckStatus
from noc.core.translation import ugettext as _


@state_handler
class DiscoveredObjectApplication(ExtDocApplication):
    """
    Discovered Object
    """

    title = _("Discovered Object")
    menu = _("Discovered Object")
    icon = "icon_monitor"
    model = DiscoveredObject
    default_ordering = ["address"]
    query_fields = ["address", "description", "hostname"]  # Use all unique fields by default
    query_condition = "contains"

    def instance_to_dict_list(self, o, fields=None, nocustom=False):
        if isinstance(o, CheckStatus):
            if not o.port:
                return o.name
            return f"{o.name}:{o.port}"
        return super().instance_to_dict_list(o, fields, nocustom)

    def instance_to_dict(self, o, fields=None, nocustom=False):
        r = super().instance_to_dict(o, fields, nocustom)
        if "checks" in r:
            r["checks"] = [f"{c.name}:{c.port}" if c.port else c.name for c in o.checks if c.status]
        # if isinstance(o, CheckStatus):
        #    if not o.port:
        #        return o.name
        #    return f"{o.name}:{o.port}"
        return r
