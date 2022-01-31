# ----------------------------------------------------------------------
# Rotek.BT.get_interfaces
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.validators import is_float
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
                            "subinterfaces": [],
                        }
                    ]
                }
            ]
        raise NotImplementedError

    def execute_snmp(self):
        interfaces = []
        try:
            ifindex = self.snmp.get("1.3.6.1.2.1.2.2.1.1.1")
            name = self.snmp.get(mib["IF-MIB::ifDescr", ifindex])
            mac = self.snmp.get(mib["IF-MIB::ifPhysAddress", ifindex])
            a_status = self.snmp.get(mib["IF-MIB::ifAdminStatus", ifindex])
            o_status = self.snmp.get(mib["IF-MIB::ifOperStatus", ifindex])
            interfaces += [
                {
                    "type": "physical",
                    "name": name,
                    "mac": mac,
                    "admin_status": True if a_status == 7 else False,
                    "oper_status": True if o_status == 1 else False,
                    "subinterfaces": [],
                }
            ]
        except Exception:
            mac = self.scripts.get_chassis_id()[0].get("first_chassis_mac")
            interfaces += [
                {
                    "type": "physical",
                    "name": "st",
                    "mac": mac if mac else None,
                    "admin_status": True,
                    "oper_status": True,
                    "subinterfaces": [],
                }
            ]
        if self.is_4250lsr:
            return interfaces
        for index in self.profile.PORT_TYPE.keys():
            s_status = 0
            status = self.snmp.get("1.3.6.1.4.1.41752.5.15.1.%s.0" % index)
            if index == 1 and int(status) == 0:
                s_status = 1
            elif index == 2:
                if is_float(status) and (-55 < float(status) < 600):
                    s_status = 1
            elif index in [4, 6] and float(status) > 0:
                s_status = 1
            elif index == 9 and int(status) != 2:
                s_status = 1
            interfaces += [
                {
                    "type": "physical",
                    "name": self.profile.IFACE_NAME.get(index),
                    "admin_status": s_status,
                    "oper_status": s_status,
                    "snmp_ifindex": index,
                    "description": self.profile.PORT_TYPE.get(index),
                    "subinterfaces": [],
                }
            ]

        return [{"interfaces": interfaces}]
