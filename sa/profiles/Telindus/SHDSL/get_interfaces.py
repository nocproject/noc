# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Telindus.SHDSL.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.sa.interfaces.base import MACAddressParameter


class Script(BaseScript):
    name = "Telindus.SHDSL.get_interfaces"
    interface = IGetInterfaces
    cache = True

    INTERFACE_TYPES = {
        "lan": "physical",  # No comment
        "wan": "unknown",  # No comment
        "sof": "loopback",  # No comment
        "bri": "physical",  # No comment
        "BR_": "unknown",  # No comment
        "tun": "tunnel",  # No comment
        "Lin": "unknown"
    }

    @classmethod
    def get_interface_type(cls, name):
        c = cls.INTERFACE_TYPES.get(name[:3])
        return c

    def execute(self):
        interfaces = []
        # Try SNMP first
        if self.has_snmp():
            try:
                for v in self.snmp.getnext("1.3.6.1.2.1.2.2.1.1", cached=True):
                    i = v[1]
                    name = self.snmp.get("1.3.6.1.2.1.2.2.1.2." + str(i))
                    if name.lower().startswith("line"):
                        continue
                    iftype = self.get_interface_type(name)
                    if not name:
                        self.logger.info(
                            "Ignoring unknown interface type: '%s", iftype
                        )
                        continue
                    s = self.snmp.get("1.3.6.1.2.1.2.2.1.6." + str(i))
                    if s:
                        mac = MACAddressParameter().clean(s)
                    astat = self.snmp.get("1.3.6.1.2.1.2.2.1.7." + str(i))
                    if astat == 1:
                        a_stat = True
                    else:
                        a_stat = False
                    ostat = self.snmp.get("1.3.6.1.2.1.2.2.1.8." + str(i))
                    if ostat == 1:
                        o_stat = True
                    else:
                        o_stat = False
                    # print repr("%s\n" % admin_status)
                    interfaces += [{
                        "type": iftype,
                        "name": name.replace("softwareLoopback", "lo"),
                        "mac": mac,
                        "admin_status": a_stat,
                        "oper_status": o_stat,
                        "ifindex": i,
                        "subinterfaces": [{
                            "name": name.replace("softwareLoopback", "lo"),
                            "admin_status": a_stat,
                            "oper_status": o_stat,
                            "mac": mac,
                            "ifindex": i,
                            "enabled_afi": ["BRIDGE"]
                        }]
                    }]
                return [{"interfaces": interfaces}]
            except self.snmp.TimeOutError:
                pass
