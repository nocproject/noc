# ---------------------------------------------------------------------
# inv.firmwarepolicy application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.translation import ugettext as _
from noc.inv.models.firmwarepolicy import FirmwarePolicy
from noc.services.web.base.extdocapplication import ExtDocApplication


class FirmwarePolicyApplication(ExtDocApplication):
    """
    FirmwarePolicy application
    """

    title = _("Firmware Policy")
    menu = [_("Setup"), _("Firmware Policy")]
    model = FirmwarePolicy
