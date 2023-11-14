# ---------------------------------------------------------------------
# cm.configurationparam application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.cm.models.configurationparam import ConfigurationParam
from noc.core.translation import ugettext as _


class SupplierApplication(ExtDocApplication):
    """
    Configuration Param application
    """

    title = _("Configuration Param")
    menu = [_("Configuration Params")]
    model = ConfigurationParam
    query_fields = ["name__icontains"]
