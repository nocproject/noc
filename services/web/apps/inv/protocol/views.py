# ----------------------------------------------------------------------
# inv.protocol application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.inv.models.protocol import Protocol
from noc.core.translation import ugettext as _


class PlatformApplication(ExtDocApplication):
    """
    Platform application
    """

    title = "Platform"
    menu = [_("Setup"), _("Protocols")]
    model = Protocol
    query_fields = ["code__icontains", "name__icontains", "description__icontains"]
    default_ordering = ["code"]
