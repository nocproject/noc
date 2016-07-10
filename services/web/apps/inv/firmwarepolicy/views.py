# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.firmwarepolicy application
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.inv.models.firmwarepolicy import FirmwarePolicy


class FirmwarePolicyApplication(ExtDocApplication):
    """
    FirmwarePolicy application
    """
    title = "FirmwarePolicy"
    menu = "Setup | Firmware Policy"
    model = FirmwarePolicy
