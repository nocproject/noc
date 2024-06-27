# ---------------------------------------------------------------------
# sa.objectdiscoveryrule application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.sa.models.objectdiscoveryrule import ObjectDiscoveryRule, CheckItem
from noc.core.translation import ugettext as _


class ObjectDiscoveryRuleApplication(ExtDocApplication):
    """
    Discovered Object
    """

    title = _("Object Discovered Rules")
    menu = [_("Setup"), _("Object Discovered Rules")]
    model = ObjectDiscoveryRule
    query_fields = ["name__icontains", "description__icontains"]
    default_ordering = ["name"]

    def instance_to_dict(self, o, fields=None, nocustom=False):
        r = super().instance_to_dict(o, fields=fields, nocustom=nocustom)
        if isinstance(o, CheckItem):
            r["check__label"] = r["check"]
        return r
