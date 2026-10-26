# ---------------------------------------------------------------------
# AlliedTelesis.AT9400.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.interfaces.igetinventory import IGetInventory
from noc.sa.profiles.Generic.get_inventory import Script as BaseScript


class Script(BaseScript):
    name = "AlliedTelesis.AT9400.get_inventory"
    interface = IGetInventory
