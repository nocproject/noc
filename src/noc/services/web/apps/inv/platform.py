# ----------------------------------------------------------------------
# inv.platform application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.translation import ugettext as _
from noc.inv.models.platform import Platform
from noc.services.web.base.extdocapplication import ExtDocApplication


class PlatformApplication(ExtDocApplication):
    """
    Platform application
    """

    title = "Platform"
    menu = [_("Setup"), _("Platforms")]
    model = Platform
    query_fields = ["full_name__icontains", "name__icontains", "description__icontains"]
    default_ordering = ["full_name"]
