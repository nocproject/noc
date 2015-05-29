# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Eltex.PON.add_vlan
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
## NOC modules
import noc.sa.script
from noc.sa.interfaces import IAddVlan


class Script(noc.sa.script.Script):
    name = "Eltex.PON.add_vlan"
    implements = [IAddVlan]

    def execute(self, vlan_id, name, tagged_ports):
        """
        # Try snmp first
        #
        #
        # See bug NOC-291: http://bt.nocproject.org/browse/NOC-291
        #
        #
        if self.snmp and self.access_profile.snmp_rw:
            try:
                if not self.scripts.has_vlan(vlan_id=vlan_id):
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
        """

        # Fallback to CLI
        with self.profile.switch(self):
#            with self.configure():  # Fix BUG...
                self.cli("configure\r")  # Fix BUG...
                self.cli("vlan %d\r" % vlan_id)
                if name:
                    self.cli("name %s\r" % name)
                if tagged_ports:
                    for port in tagged_ports:
                        self.cli("tagged %s\r" % port)
                self.cli("exit\r")  # Fix BUG...
                self.cli("exit\r")  # Fix BUG...
        self.save_config()
        return True
