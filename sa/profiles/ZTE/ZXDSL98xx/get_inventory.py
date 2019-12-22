# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ZTE.ZXDSL98xx.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_inventory import Script as BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "ZTE.ZXDSL98xx.get_inventory"
    interface = IGetInventory
