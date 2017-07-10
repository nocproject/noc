# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# inv.firmware application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication, view
from noc.inv.models.firmware import Firmware
from noc.core.translation import ugettext as _


class FirmwareApplication(ExtDocApplication):
    """
    Firmware application
    """
    title = _("Firmware")
    menu = [_("Setup"), _("Firmware")]
    model = Firmware
