# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Ruckus.ZoneDirector.get_cpe
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetcpe import IGetCPE
from noc.sa.interfaces.base import MACAddressParameter


class Script(BaseScript):
    name = "Ruckus.ZoneDirector.get_cpe"
    interface = IGetCPE

    type_map = {
        "0": "inactive",
        "1": "active",
        "2": "approval",
        "3": "other",
        "4": "provisioning"
    }

    def execute(self):
        r = []
        if self.has_snmp():
            try:
                for v in self.snmp.getnext("1.3.6.1.4.1.25053.1.2.2.4.1.1.1.1.5"):
                    cpename = v[1]
                    cpeid = v[0][len("1.3.6.1.4.1.25053.1.2.2.4.1.1.1.1.5") + 1:]
                    # cpename = self.snmp.get("1.3.6.1.4.1.25053.1.2.2.4.1.1.1.1.5." + cpeid)
                    s = str(self.snmp.get("1.3.6.1.4.1.25053.1.2.2.4.1.1.1.1.2.%s" % cpeid))
                    mac = MACAddressParameter().clean(s)  # convert mac
                    # print "%s\n" % mac
                    key = ".".join(str(int(x, 16)) for x in mac.split(":"))  # convert mac - > bytes
                    # print "%s\n" % key
                    status = self.snmp.get("1.3.6.1.4.1.25053.1.2.2.1.1.2.1.1.3.6.%s" % key)
                    ip = self.snmp.get("1.3.6.1.4.1.25053.1.2.2.1.1.2.1.1.10.6.%s" % key)
                    location = self.snmp.get("1.3.6.1.4.1.25053.1.2.2.4.1.1.1.1.7.%s" % cpeid)
                    description = self.snmp.get("1.3.6.1.4.1.25053.1.2.2.1.1.2.1.1.2.6.%s" % key)
                    sn = self.snmp.get("1.3.6.1.4.1.25053.1.2.2.1.1.2.1.1.5.6.%s" % key)
                    model = self.snmp.get("1.3.6.1.4.1.25053.1.2.2.1.1.2.1.1.4.6.%s" % key)
                    version = self.snmp.get("1.3.6.1.4.1.25053.1.2.2.1.1.2.1.1.7.6.%s" % key)
                    r.append({
                        "vendor": "Ruckus",
                        "model": model,
                        "version": version,
                        "mac": mac,
                        "status": self.type_map[str(status)],
                        "id": cpeid,
                        "global_id": mac,
                        "type": "ap",
                        "name": cpename,
                        "ip": ip,
                        "serial": sn,
                        "description": description,
                        "location": location
                    })
                    # print ("%s\n" % r)
                return r
            except self.snmp.TimeOutError:
                pass
