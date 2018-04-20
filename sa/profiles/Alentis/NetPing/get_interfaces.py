# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Alentis.NetPing.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4


class Script(BaseScript):
    name = "Alentis.NetPing.get_interfaces"
    interface = IGetInterfaces
=======
##----------------------------------------------------------------------
## Alentis.NetPing.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaces
from noc.lib.ip import IPv4


class Script(NOCScript):
    name = "Alentis.NetPing.get_interfaces"
    implements = [IGetInterfaces]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def execute(self):

        data = self.profile.var_data(self, "/setup_get.cgi")
        ip = data["ip"].encode('UTF8')
        mask = IPv4.netmask_to_len(data["mask"].encode('UTF8'))

        iface = {
            "name": 'Fa1',
            "admin_status": True,
            "oper_status": True,
            "type": "physical",
            "description": data["location"].encode('UTF8'),
            "mac": data["mac"].encode('UTF8'),
            "subinterfaces": [{
                "name": 'Fa1',
                "admin_status": True,
                "oper_status": True,
                "type": "physical",
                "description": data["hostname"].encode('UTF8'),
                "mac": data["mac"].encode('UTF8'),
                "enabled_afi": ["IPv4"],
                "ipv4_addresses": ["%s/%s" % (ip, mask)]
                }]
            }
        return [{"interfaces": [iface]}]
