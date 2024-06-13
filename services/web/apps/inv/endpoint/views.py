# ----------------------------------------------------------------------
# inv.endpoint application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.inv.models.endpoint import Endpoint
from noc.core.translation import ugettext as _


class EndpointApplication(ExtDocApplication):
    """
    Endpoint application
    """

    title = "Endpoint"
    menu = [_("Setup"), _("Endpoints")]
    model = Endpoint
    glyph = "bullseye"
