# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.firmware application
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.inv.models.firmware import Firmware


class FirmwareApplication(ExtDocApplication):
    """
    Firmware application
    """
    title = "Firmware"
    menu = "Setup | Firmware"
    model = Firmware
