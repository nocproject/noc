# ---------------------------------------------------------------------
# cm.configurationscope application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.cm.models.configurationscope import ConfigurationScope
from noc.core.translation import ugettext as _


class ConfigurationScopApplication(ExtDocApplication):
    """
    Configuration Scope application
    """

    title = _("Configuration Scope")
    menu = [_("Setup"), _("Configuration Scope")]
    model = ConfigurationScope
    query_fields = ["name__icontains"]
