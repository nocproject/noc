# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# inv.firmwarepolicy application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.translation import ugettext as _
from noc.inv.models.firmwarepolicy import FirmwarePolicy
# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication


class FirmwarePolicyApplication(ExtDocApplication):
    """
    FirmwarePolicy application
    """
    title = _("Firmware Policy")
    menu = [_("Setup"), _("Firmware Policy")]
    model = FirmwarePolicy
