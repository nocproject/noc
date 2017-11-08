# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Ruckus.SmartZone.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
# Python modules
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "Ruckus.SmartZone.get_interfaces"
    interface = IGetInterfaces
    cache = True

    INTERFACE_TYPES = {

        "lo": "loopback",  # Loopback
        "br": "unknown",  # No comment

    }

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
        c = cls.INTERFACE_TYPES.get(name[:2])
        return c

    def execute(self):
        interfaces = []
        # Try SNMP first
        if self.has_snmp():
            try:
                for v in self.snmp.getnext("1.3.6.1.2.1.2.2.1.1", cached=True):
                    i = v[1]
                    name = self.snmp.get("1.3.6.1.2.1.2.2.1.2.%s" % str(i))
                    iftype = self.get_interface_type(name)
                    if not name:
                        self.logger.info(
                            "Ignoring unknown interface type: '%s", iftype
                        )
                        continue
                    mac = self.snmp.get("1.3.6.1.2.1.2.2.1.6.%s" % str(i))
                    status = self.snmp.get("1.3.6.1.2.1.2.2.1.7.%s" % str(i))
                    if status == 1:
                        admin_status = "up"
                    else:
                        admin_status = "down"
                    # print repr("%s\n" % admin_status)
                    interfaces += [{
                        "type": iftype,
                        "name": name,
                        "mac": mac,
                        "admin_status": (admin_status).lower() == "up",
                        "subinterfaces": [{
                            "name": name,
                            "mac": mac,
                            "enabled_afi": ["BRIDGE"]
                        }]
                    }]
                return [{"interfaces": interfaces}]
            except self.snmp.TimeOutError:
                pass
