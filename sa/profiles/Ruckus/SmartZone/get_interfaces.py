# ---------------------------------------------------------------------
# Ruckus.SmartZone.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.mib import mib


class Script(BaseScript):
    name = "Ruckus.SmartZone.get_interfaces"
    interface = IGetInterfaces
    cache = True

    INTERFACE_TYPES = {"lo": "loopback", "br": "unknown"}  # Loopback  # No comment

    INTERFACE_TYPES2 = {
        "eth": "physical",  # No comment
        "vEt": "other",  # No comment
        "pca": "physical",  # No comment
        "pow": "physical",  # No comment
    }

    @classmethod
    def get_interface_type(cls, name):
        c = cls.INTERFACE_TYPES2.get(name[:3])
        if c:
            return c
        return cls.INTERFACE_TYPES.get(name[:2])

    def execute_snmp(self, **kwargs):
        interfaces = []
        # Try SNMP first
        for v in self.snmp.getnext("1.3.6.1.2.1.2.2.1.1", cached=True):
            i = v[1]
            name = self.snmp.get(mib["IF-MIB::ifDescr", i])
            iftype = self.get_interface_type(name)
            if not name:
                self.logger.info("Ignoring unknown interface type: '%s", iftype)
                continue
            mac = self.snmp.get(mib["IF-MIB::ifPhysAddress", i])
            status = self.snmp.get(mib["IF-MIB::ifAdminStatus", i])
            if status == 1:
                admin_status = "up"
            else:
                admin_status = "down"
            # print repr("%s\n" % admin_status)
            interfaces += [
                {
                    "type": iftype,
                    "name": name,
                    "mac": mac,
                    "admin_status": (admin_status).lower() == "up",
                    "subinterfaces": [{"name": name, "mac": mac, "enabled_afi": ["BRIDGE"]}],
                }
            ]
        return [{"interfaces": interfaces}]
