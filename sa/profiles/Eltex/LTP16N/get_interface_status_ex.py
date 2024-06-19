# ---------------------------------------------------------------------
# Eltex.LTP16N.get_ifindexes
# ---------------------------------------------------------------------
# Copyright (C) 2024-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_interface_status_ex import Script as BaseScript
from noc.sa.interfaces.igetinterfacestatusex import IGetInterfaceStatusEx


class Script(BaseScript):
    name = "Eltex.LTP16N.get_interface_status_ex"
    interface = IGetInterfaceStatusEx

    def execute_snmp(self, **kwargs):
        interfaces_ex = []
        interfaces = self.scripts.get_interface_status()
        ifname = self.scripts.get_ifindexes()
        n = self.profile.get_count_pon_ports(self)  # PON-ports

        for i in interfaces:
            if i["interface"].split(" ")[0] == "front-port":
                v = self.snmp.get(
                    f"1.3.6.1.4.1.35265.1.209.1.6.2.1.3.{int(ifname[i['interface']]) - n}"
                )
                iface = {
                    "interface": i["interface"],
                    "oper_status": i["status"],
                    "admin_status": i["status"],
                    "full_duplex": True,
                    "in_speed": int(v) * 1000,
                    "out_speed": int(v) * 1000,
                }
            elif i["interface"].split(" ")[0] == "pon-port":
                iface = {
                    "interface": i["interface"],
                    "oper_status": i["status"],
                    "admin_status": i["status"],
                    "full_duplex": True,
                    "in_speed": 1250000,
                    "out_speed": 2500000,
                }
            else:
                iface = {
                    "interface": i["interface"],
                    "oper_status": i["status"],
                    "admin_status": i["status"],
                    "full_duplex": True,
                }
            interfaces_ex += [iface]
        return interfaces_ex
