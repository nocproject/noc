# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AlliedTelesis.AT9900.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVlans


class Script(NOCScript):
    name = "AlliedTelesis.AT9900.get_vlans"
    implements = [IGetVlans]
    rx_vlan_name_line = re.compile(r"^\sName\s\.*\s(?P<name>\S+)", re.MULTILINE)
    rx_vlan_id_line = re.compile(r"^\sIdentifier\s\.*\s(?P<vlan_id>\d{1,4})", re.MULTILINE)

    def execute(self):
        vlans = self.cli("show vlan")
        r = []
        for l in vlans.split("\n"):
            match_name = self.rx_vlan_name_line.match(l)
            if match_name:
                name = match_name.group("name")
                match_id = self.rx_vlan_id_line.match(l)
                if match_id:
                    vlan_id = int(match_id.group("vlan_id"))
                    r += [{"name": name, "vlan_id": vlan_id}]
        return r
