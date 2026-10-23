# ---------------------------------------------------------------------
# AcmePacket.NetNet.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "AcmePacket.NetNet.get_interfaces"
    interface = IGetInterfaces

    MAX_REPETITIONS = 20
    MAX_GETNEXT_RETIRES = 1

    def get_switchport(self):
        return {}

    def get_portchannels(self):
        return {}

    def get_ip_ifaces(self):
        # Stuck SNMP when getting oids
        return {}
