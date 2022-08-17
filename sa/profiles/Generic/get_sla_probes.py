# ---------------------------------------------------------------------
# Generic.get_sla_probes
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from collections import defaultdict

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetslaprobes import IGetSLAProbes
from noc.core.mib import mib


class Script(BaseScript):
    name = "Generic.get_sla_probes"
    interface = IGetSLAProbes

    probes_snmp_type_map = {
        6: "icmp-echo",
    }

    def execute_snmp(self, **kwargs):
        probes = defaultdict(dict)
        index_map = {}
        for index, address, descr, rtt_type, status in self.snmp.get_tables(
            [
                mib["DISMAN-PING-MIB::pingCtlTargetAddress"],
                mib["DISMAN-PING-MIB::pingCtlDescr"],
                mib["DISMAN-PING-MIB::pingCtlType"],
                mib["DISMAN-PING-MIB::pingCtlRowStatus"],
            ],
            bulk=False,
        ):
            if rtt_type not in self.probes_snmp_type_map:
                self.logger.info("[%s] Unknown Probe type: %s. Skipping...", index, rtt_type)
                continue
            if index not in index_map:
                index_s = index.split(".")
                index_map[index] = {
                    "owner": "".join([chr(int(x)) for x in index_s[1 : int(index_s[0]) + 1]]),
                    "test_name": "".join([chr(int(x)) for x in index_s[int(index_s[0]) + 2 :]]),
                }
            probes[index] = {
                "name": index_map[index]["test_name"],
                "owner": index_map[index]["owner"],
                "status": status,
                "type": self.probes_snmp_type_map[rtt_type],
            }
            if descr:
                probes[index]["description"] = descr
            probes[index]["target"] = address

        return list(probes.values())
