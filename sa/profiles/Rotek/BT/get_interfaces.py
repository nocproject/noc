# ----------------------------------------------------------------------
# Rotek.BT.get_interfaces
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.mib import mib


class Script(BaseScript):
    name = "Rotek.BT.get_interfaces"
    interface = IGetInterfaces

    def execute_cli(self, **kwargs):
        if self.is_4250lsr:
            v = self.http.get("/info.cgi?_", json=True, cached=True, eof_mark=b"}")
            return [
                {
                    "interfaces": [
                        {
                            "type": "physical",
                            "name": "eth0",
                            "mac": v["macaddr"],
                            "hints": ["noc::interface::role::uplink"],
                            "subinterfaces": [],
                        }
                    ]
                }
            ]
        raise NotImplementedError

    def execute_snmp(self):
        try:
            ifindex = self.snmp.get("1.3.6.1.2.1.2.2.1.1.1")
            name = self.snmp.get(mib["IF-MIB::ifDescr", ifindex])
            mac = self.snmp.get(mib["IF-MIB::ifPhysAddress", ifindex])
            a_status = self.snmp.get(mib["IF-MIB::ifAdminStatus", ifindex])
            o_status = self.snmp.get(mib["IF-MIB::ifOperStatus", ifindex])
            interfaces = [
                {
                    "type": "physical",
                    "name": name,
                    "mac": mac,
                    "admin_status": a_status == 7,
                    "oper_status": o_status == 1,
                    "hints": ["noc::interface::role::uplink"],
                    "subinterfaces": [],
                }
            ]
        except Exception:
            mac = self.scripts.get_chassis_id()[0].get("first_chassis_mac")
            interfaces = [
                {
                    "type": "physical",
                    "name": "st",
                    "mac": mac if mac else None,
                    "admin_status": True,
                    "oper_status": True,
                    "hints": ["noc::interface::role::uplink"],
                    "subinterfaces": [],
                }
            ]

        return [{"interfaces": interfaces}]
