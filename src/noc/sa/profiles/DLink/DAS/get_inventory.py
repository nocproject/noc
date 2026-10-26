# ---------------------------------------------------------------------
# DLink.DAS.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.interfaces.igetinventory import IGetInventory
from noc.sa.profiles.Generic.get_inventory import Script as BaseScript


class Script(BaseScript):
    name = "DLink.DAS.get_inventory"
    interface = IGetInventory
