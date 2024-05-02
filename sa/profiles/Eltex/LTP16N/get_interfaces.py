# ---------------------------------------------------------------------
# Eltex.LTP16N.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2024-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "Eltex.LTP16N.get_interfaces"
    interface = IGetInterfaces

    def execute_snmp(self, **kwargs):
        interfaces = []
        ifname = self.scripts.get_ifindexes()
        ifname = {value: key for key, value in ifname.items()}

        if self.capabilities["SNMP | OID | sysDescr"] == "ELTEX LTP-16N":
            N = 16
        else:
            N = 8

        # PON-port
        ifstatus = {}
        for oid, v in self.snmp.getnext("1.3.6.1.4.1.35265.1.209.4.3.1.1.3", cached=True):
            sindex = oid[len("1.3.6.1.4.1.35265.1.209.4.3.1.1.3") + 1 :].split(".")[1]
            if v == 4:
                v = True
            else:
                v = False
            ifstatus[str(sindex)] = v

        # Front-port
        for oid, v in self.snmp.getnext("1.3.6.1.4.1.35265.1.209.1.6.2.1.2", cached=True):
            sindex = oid[len("1.3.6.1.4.1.35265.1.209.1.6.2.1.2") + 1 :]
            sindex = int(sindex) + N
            if v == 1:
                v = True
            else:
                v = False
            ifstatus[str(sindex)] = v

        ifdescr = {}
        for oid, v in self.snmp.getnext("1.3.6.1.4.1.35265.1.209.1.6.4.1.5", cached=True):
            sindex = oid[len("1.3.6.1.4.1.35265.1.209.1.6.4.1.5") + 1 :]
            sindex = int(sindex) + N
            ifdescr[str(sindex)] = v

        for i in ifname:
            iface = {
                "name": ifname[i],
                "type": "physical",
                "admin_status": ifstatus[i],
                "oper_status": ifstatus[i],
                "description": ifdescr.get(i),
                "snmp_ifindex": i,
                "subinterfaces": [
                    {
                        "name": ifname[i],
                        "admin_status": ifstatus[i],
                        "oper_status": ifstatus[i],
                        "enabled_afi": ["BRIDGE"],
                        "snmp_ifindex": i,
                    }
                ],
            }

            interfaces += [iface]
        return [{"interfaces": interfaces}]
