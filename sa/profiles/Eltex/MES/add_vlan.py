# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Eltex.MES.add_vlan
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
## NOC modules
import noc.sa.script
from noc.sa.interfaces import IAddVlan


class Script(noc.sa.script.Script):
    name = "Eltex.MES.add_vlan"
    implements = [IAddVlan]

    def execute(self, vlan_id, name, tagged_ports):
        a = ''
        if not self.scripts.has_vlan(vlan_id=vlan_id):
            a = 1
        if tagged_ports:
            ports = ''
            for port in tagged_ports:
                if ports:
                    ports = ports + ',' + port
                else:
                    ports = port
            tagged = ports

        # Try snmp first
        #
        #
        # See bug NOC-291: http://bt.nocproject.org/browse/NOC-291
        #
        #
#        if self.snmp and self.access_profile.snmp_rw:
#            try:
#                if a:
#                    oid = "1.3.6.1.2.1.17.7.1.4.3.1.1." + str(vlan_id)
#                    self.snmp.set(oid, name)
#                    oid = "1.3.6.1.2.1.17.7.1.4.3.1.5." + str(vlan_id)
#                    self.snmp.set(oid, 1)  # or 4
#                if tagged:
#                    oid = "1.3.6.1.2.1.17.7.1.4.3.1.1." + str(vlan_id)
#                    binports = ''
#                    for i in range(len(max(tagged))):
#                        if i in tagged:
#                            binports = binports + '1'
#                        else:
#                            binports = binports + '0'
#                    # TODO: bin_to_hex
#                    self.snmp.set(oid, self.bin_to_hex(binports))
#            except self.snmp.TimeOutError:
#                pass

        # Fallback to CLI
        with self.configure():
            if a:
                self.cli("vlan database")
                self.cli("vlan %d" % vlan_id)
                self.cli("exit")
                self.cli("interface vlan %d" % vlan_id)
                self.cli("name %s" % name)
                self.cli("exit")
            if tagged_ports:
                self.cli("interface range %s" % tagged)
### 802.1q
#                self.cli("switchport general allowed vlan add %d tagged"
#                    % vlan_id)
## trunk
                self.cli("switchport trunk allowed vlan add  %d" % vlan_id)
        self.save_config()
        return True
