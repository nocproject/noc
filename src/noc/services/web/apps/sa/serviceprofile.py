# ---------------------------------------------------------------------
# sa.serviceprofile application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.sa.models.serviceprofile import ServiceProfile
from noc.core.translation import ugettext as _


class ServiceProfileApplication(ExtDocApplication):
    """
    ServiceProfile application
    """

    title = _("Service Profile")
    menu = [_("Setup"), _("Service Profiles")]
    model = ServiceProfile
