# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.1910.get_interface_index
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetIfIndex
import re


class Script(NOCScript):
    name = "HP.1910.get_interface_index"
    implements = [IGetIfIndex]
    rx_line = re.compile(
        r"Interface = \S+, Ifindex = (?P<index>\d+)")

    def execute(self, interface):

        # Try SNMP first
        if self.has_snmp():
            try:
                interface = interface.replace('Gi ', 'GigabitEthernet')
                interface = interface.replace('Vl ', 'Vlan-interface')
                for iface in self.snmp.get_tables(["1.3.6.1.2.1.31.1.1.1.1"],
                    bulk=True):
                    if iface[1] == interface:
                        iface_index = iface[0]
                        break
                return iface_index
            except self.snmp.TimeOutError:
                pass

        """
        try:
             c = self.cli("show snmp mib ifmib ifindex %s" % interface)
         except self.CLISyntaxError:
             return None
         match = self.re_search(self.rx_line, c)
         if match:
             iface_index = int(match.group("index"))
        return iface_index
        """
        return None
