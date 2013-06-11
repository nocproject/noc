# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.1905.add_vlan
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IAddVlan


class Script(NOCScript):
    name = "HP.1905.add_vlan"
    implements = [IAddVlan]

    def execute(self, vlan_id, name, tagged_ports=[]):
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
        raise Exception("Not implemented")
        #
        #
        if self.snmp and self.access_profile.snmp_rw:
            try:
                if a:
                    oid = "1.3.6.1.2.1.17.7.1.4.3.1.1." + str(vlan_id)
                    self.snmp.set(oid, name)
                    oid = "1.3.6.1.2.1.17.7.1.4.3.1.5." + str(vlan_id)
                    self.snmp.set(oid, 1)  # or 4
                if tagged:
                    oid = "1.3.6.1.2.1.17.7.1.4.3.1.1." + str(vlan_id)
                    binports = ''
                    for i in range(len(max(tagged))):
                        if i in tagged:
                            binports = binports + '1'
                        else:
                            binports = binports + '0'
                    # TODO: bin_to_hex
                    self.snmp.set(oid, self.bin_to_hex(binports))
            except self.snmp.TimeOutError:
                pass

        # Fallback to CLI
        raise Exception("Not implemented")
