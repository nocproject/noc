# ---------------------------------------------------------------------
# Supertel.K2X.add_vlan
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iaddvlan import IAddVlan


class Script(BaseScript):
    name = "Supertel.K2X.add_vlan"
    interface = IAddVlan

    def execute(self, vlan_id, name, tagged_ports):
        a = ""
        if not self.scripts.has_vlan(vlan_id=vlan_id):
            a = 1
        ports = ""
        channels = ""
        if tagged_ports:
            for port in tagged_ports:
                if port[:2] == "ch":
                    if channels:
                        channels = channels + "," + port[2:]
                    else:
                        channels = port[2:]
                elif ports:
                    ports = ports + "," + port
                else:
                    ports = port

        """
        # Try snmp first
        #
        #
        # See bug NOC-291: http://bt.nocproject.org/browse/NOC-291
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
        """

        # Fallback to CLI
        with self.configure():
            if a:
                self.cli("vlan database")
                self.cli("vlan %d" % vlan_id)
                self.cli("exit")
                self.cli("interface vlan %d" % vlan_id)
                self.cli("name %s" % name)
                self.cli("exit")
            if ports:
                self.cli("interface range ethernet %s" % ports)
                self.cli("switchport trunk allowed vlan add %d" % vlan_id)
                self.cli("exit")
            if channels:
                self.cli("interface range port-channel %s" % channels)
                self.cli("switchport trunk allowed vlan add %d" % vlan_id)
        self.save_config()
        return True
