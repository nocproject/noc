# ---------------------------------------------------------------------
# Generic.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator

# NOC Modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans
from noc.core.mib import mib
from noc.core.comp import smart_text


class Script(BaseScript):
    name = "Generic.get_vlans"
    interface = IGetVlans

    def execute_snmp(self, **kwargs):
        result = []
        oids = {}
        # Get OID -> VLAN ID mapping
        # dot1qVlanFdbId
        for oid, v in self.snmp.getnext(mib["Q-BRIDGE-MIB::dot1qVlanFdbId"]):
            if not v:
                continue
            oids[oid.split(".")[-1]] = v
        if oids:
            # Get VLAN names
            # dot1qVlanStaticName
            for oid, v in self.snmp.getnext(mib["Q-BRIDGE-MIB::dot1qVlanStaticName"]):
                o = oid.split(".")[-1]
                result += [{"vlan_id": int(oids[o]), "name": v.strip().rstrip(smart_text("\x00"))}]
        else:
            tmp_vlan = []
            # dot1qVlanStaticName
            for oid, v in self.snmp.getnext(mib["Q-BRIDGE-MIB::dot1qVlanStaticEntry"]):
                vlan_id = int(oid.split(".")[-1])
                if vlan_id in tmp_vlan:
                    break
                result += [{"vlan_id": vlan_id, "name": v.strip().rstrip(smart_text("\x00"))}]
                tmp_vlan += [vlan_id]
        if result:
            return sorted(result, key=operator.itemgetter("vlan_id"))
        raise NotImplementedError()
