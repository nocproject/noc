# ---------------------------------------------------------------------
# sa.objectdiscoveryrule application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.sa.models.objectdiscoveryrule import ObjectDiscoveryRule
from noc.core.translation import ugettext as _


class ObjectDiscoveryRuleApplication(ExtDocApplication):
    """
    Discovered Object
    """

    title = _("Discovered Object")
    menu = _("Discovered Object")
    icon = "icon_monitor"
    model = ObjectDiscoveryRule
