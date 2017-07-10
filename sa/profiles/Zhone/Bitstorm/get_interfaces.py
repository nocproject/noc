# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Zhone.Bitstorm.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4
from noc.core.mib import mib



class Script(BaseScript):
    name = "Zhone.Bitstorm.get_interfaces"
    interface = IGetInterfaces

    def execute(self):
        v = self.cli("show interface ethernet all configuration", cached=True)
        v = v.split("\n\n\n")

        result = {'null': 'null'}
        interfaces = []

        for k in v:
            x = re.split(r'\s{2,20}', k)

            i = len(x) - 1
            while x.count('') > 0:
                if x[i].strip() == '':
                    x.pop(i)
                i -= 1

            key = x[0].strip().split(r' ')[0]
            value = x[0].strip().split(r' ')[1]
            x.pop(0)
            x.insert(0, value)
            x.insert(0, key)

            for i in range(0, len(x) - 1, 2):
                result[x[i]] = x[i + 1]

            iface = {
                "name": result.get('Port'),
                "type": "physical",
                "admin_status": result.get('state (admin status)'),
                "oper_status": result.get('state (admin status)'),
                "subinterfaces": [{
                    "name": result.get('Port'),
                    "admin_status": result.get('state (admin status)'),
                    "oper_status": result.get('state (admin status)'),
                    "vlan_ids": int(result.get('pvid')),
                    "tagged_vlans": [int(result.get('pvid'))]
                }]
            }

            interfaces += [iface]

            # print [{"interfaces": interfaces}]

        return [{"interfaces": interfaces}]