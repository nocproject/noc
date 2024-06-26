# ---------------------------------------------------------------------
# Eltex.LTP16N.get_interface_status
# ---------------------------------------------------------------------
# Copyright (C) 2024-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus


class Script(BaseScript):
    name = "Eltex.LTP16N.get_interface_status"
    interface = IGetInterfaceStatus

    def execute_snmp(self, **kwargs):
        interfaces = []
        ifname = self.scripts.get_ifindexes()
        ifname = {value: key for key, value in ifname.items()}
        n = self.profile.get_count_pon_ports(self)  # PON-ports

        # PON-port
        ifstatus = dict()
        for oid, v in self.snmp.getnext("1.3.6.1.4.1.35265.1.209.4.3.1.1.3", cached=True):
            sindex = oid[len("1.3.6.1.4.1.35265.1.209.4.3.1.1.3") + 1 :].split(".")[1]
            v = False
            if v == 4:
                v = True
            ifstatus[str(sindex)] = v

        # Front-port
        for oid, v in self.snmp.getnext("1.3.6.1.4.1.35265.1.209.1.6.2.1.2", cached=True):
            sindex = oid[len("1.3.6.1.4.1.35265.1.209.1.6.2.1.2") + 1 :]
            sindex = int(sindex) + n
            v = False
            if v == 1:
                v = True
            ifstatus[str(sindex)] = v

        for i in ifname:
            iface = {"interface": ifname[i], "status": ifstatus[i]}
            interfaces += [iface]
        return interfaces
