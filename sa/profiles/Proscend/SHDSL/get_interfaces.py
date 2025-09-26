# ---------------------------------------------------------------------
# Proscend.SHDSL.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.sa.interfaces.base import MACAddressParameter
from noc.core.mib import mib


class Script(BaseScript):
    name = "Proscend.SHDSL.get_interfaces"
    interface = IGetInterfaces
    cache = True

    INTERFACE_TYPES = {
        "lan": "physical",  # No comment
        "mgm": "unknown",  # No comment
        "loo": "loopback",  # No comment
        "shd": "physical",  # No comment
    }

    @classmethod
    def get_interface_type(cls, name):
        return cls.INTERFACE_TYPES.get(name[:3].lower())

    def execute(self):
        interfaces = []
        mac = []
        # Try SNMP first
        if self.has_snmp():
            try:
                for v in self.snmp.getnext("1.3.6.1.2.1.2.2.1.1", cached=True):
                    i = v[1]
                    name = self.snmp.get(mib["IF-MIB::ifDescr", i])
                    iftype = self.get_interface_type(name)
                    if not name:
                        self.logger.info("Ignoring unknown interface type: '%s", iftype)
                        continue
                    s = self.snmp.get(mib["IF-MIB::ifPhysAddress", i])
                    if s:
                        mac = MACAddressParameter().clean(s)
                    astat = self.snmp.get(mib["IF-MIB::ifAdminStatus", i])
                    if astat == 1:
                        a_stat = True
                    else:
                        a_stat = False
                    ostat = self.snmp.get(mib["IF-MIB::ifOperStatus", i])
                    if ostat == 1:
                        o_stat = True
                    else:
                        o_stat = False
                    # print repr("%s\n" % admin_status)
                    interfaces += [
                        {
                            "type": iftype,
                            "name": name,
                            "mac": mac,
                            "admin_status": a_stat,
                            "oper_status": o_stat,
                            "ifindex": i,
                            "subinterfaces": [
                                {
                                    "name": name,
                                    "admin_status": a_stat,
                                    "oper_status": o_stat,
                                    "mac": mac,
                                    "ifindex": i,
                                    "enabled_afi": ["BRIDGE"],
                                }
                            ],
                        }
                    ]
                return [{"interfaces": interfaces}]
            except self.snmp.TimeOutError:
                pass
