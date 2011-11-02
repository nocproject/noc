# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## OS.Linux.get_staticvlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.staticvlan.models import ranges_to_list_str
from noc.sa.interfaces import IGetStaticVlans
from noc.staticvlan.models import topo2port

rx_vlan = re.compile(r"^\S+\s+\|+\s+(?P<vlan>\d+)\s+\|+\s+(?P<interface>\S+)+$", re.MULTILINE)

class Script(NOCScript):
    name = "OS.Linux.get_staticvlans"
    implements = [IGetStaticVlans]

    def execute(self):
        rv = {}
        for vlan in rx_vlan.finditer(self.cli("cat /proc/net/vlan/config")):
            vlan_id = vlan.group("vlan")
# TODO vlan name... Looking for way find vlan name in GNU/Linux and *BSD
            name = 'br' + vlan_id
            if vlan_id not in rv:
                rv.update({ vlan_id : {
                                    "name"      : name,
                                    "tagged"    : [],
                                    "untagged"  : [],
                                    "forbidden" : [],
                                    }
                                    })
# TODO untagged, forbidden if it posible
            rv[vlan_id]["tagged"].append(topo2port(vlan.group("interface")))

# Some device use /etc/config/vlan.rules for configure vlans (Eltex TAU-*).
        if rv == {}:
            vlan = self.cli("cat /etc/config/vlan.rules 2>/dev/null").strip()
            if vlan:
                vlan = vlan.split('\n')
                for i in range(len(vlan)):
                    l = vlan[i].split(' ')
                    rv.update({ l[0] : {
                                        "name"      : "br" + l[0],
                                        "tagged"    : [],
                                        "untagged"  : [],
                                        "forbidden" : [],
                                        }
                                        })
                    for j in range(len(l) - 1):
                        interface = j + 1
                        if l[interface] == '1' or l[interface] == '0':
                            pass
                        elif l[interface] == '2':
                            rv[l[0]]["untagged"].append(str(interface))
                        elif l[interface] == '3':
                            rv[l[0]]["tagged"].append(str(interface))

        r=[]
        for vlan_id in rv:
            r.append({
                    "vlan"          : vlan_id,
                    "name"          : rv[vlan_id]["name"],
                    "tagged"        : ", ".join(rv[vlan_id]["tagged"]),
                    "untagged"      : ", ".join(rv[vlan_id]["untagged"]),
                    "forbidden"     : ", ".join(rv[vlan_id]["forbidden"]),
                    "advertisement" : False,
                    })
#        if not r:
#            raise Exception("Not implemented")
        return r
