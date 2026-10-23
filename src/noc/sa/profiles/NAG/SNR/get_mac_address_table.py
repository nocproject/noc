# ---------------------------------------------------------------------
# NAG.SNR.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_mac_address_table import Script as BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable


class Script(BaseScript):
    name = "NAG.SNR.get_mac_address_table"
    interface = IGetMACAddressTable
