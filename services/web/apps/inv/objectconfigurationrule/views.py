# ---------------------------------------------------------------------
# inv.objectconfigurationrule application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.inv.models.objectconfigurationrule import ObjectConfigurationRule
from noc.core.translation import ugettext as _


class ObjectConfigurationRuleApplication(ExtDocApplication):
    """
    Configuration Rule application
    """

    title = _("Configuration Rules")
    menu = [_("Setup"), _("Configuration Rules")]
    model = ObjectConfigurationRule
    query_fields = ["name__icontains"]
