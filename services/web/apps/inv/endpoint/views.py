# ----------------------------------------------------------------------
# inv.endpoint application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.inv.models.endpoint import Endpoint
from noc.core.translation import ugettext as _
from noc.core.feature import Feature


class EndpointApplication(ExtDocApplication):
    """
    Endpoint application
    """

    title = "Endpoint"
    menu = [_("Setup"), _("Endpoints")]
    model = Endpoint
    glyph = "bullseye"
    field_labels = Feature.CHANNEL
    require_feature = Feature.CHANNEL
