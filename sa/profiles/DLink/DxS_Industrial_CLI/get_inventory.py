# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DLink.DxS_Industrial_CLI.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_inventory import Script as BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "DLink.DxS_Industrial_CLI.get_inventory"
    interface = IGetInventory
