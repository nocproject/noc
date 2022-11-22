# ---------------------------------------------------------------------
# peer.rir application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extmodelapplication import ExtModelApplication
from noc.peer.models.rir import RIR
from noc.core.translation import ugettext as _


class RIRApplication(ExtModelApplication):
    """
    RIR application
    """

    title = _("RIR")
    menu = [_("Setup"), _("RIRs")]
    model = RIR
