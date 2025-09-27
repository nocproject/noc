# ---------------------------------------------------------------------
# Huawei.VRP.get_sla_probes
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from collections import defaultdict

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetslaprobes import IGetSLAProbes
from noc.core.mib import mib


class Script(BaseScript):
    name = "Huawei.VRP.get_sla_probes"
    interface = IGetSLAProbes

    probes_snmp_type_map = {
        5: "udp-jitter",
        6: "icmp-echo",
    }

    def execute_snmp(self, **kwargs):
        probes = defaultdict(dict)
        index_map = {}
        for index, tag, rtt_type, status in self.snmp.get_tables(
            [
                mib["NQA-MIB::nqaAdminCtrlTag"],
                mib["NQA-MIB::nqaAdminCtrlType"],
                mib["NQA-MIB::nqaAdminCtrlStatus"],
            ],
            bulk=False,
        ):
            if rtt_type not in self.probes_snmp_type_map:
                self.logger.info("[%s] Unknown Probe type: %s. Skipping...", index, rtt_type)
                continue
            if index not in index_map:
                index_s = index.split(".")
                index_map[index] = {
                    "admin_name": "".join([chr(int(x)) for x in index_s[1 : int(index_s[0]) + 1]]),
                    "test_name": "".join([chr(int(x)) for x in index_s[int(index_s[0]) + 2 :]]),
                }
            probes[index] = {
                "name": index_map[index]["test_name"],
                "group": index_map[index]["admin_name"],
                "status": status,
                "type": self.probes_snmp_type_map[rtt_type],
            }
            if tag:
                probes[index]["tags"] = [f"noc::sla::tag::{tag}"]
        for index, target, target_port, tos, vrf in self.snmp.get_tables(
            [
                mib["NQA-MIB::nqaAdminParaTargetAddress"],
                mib["NQA-MIB::nqaAdminParaTargetPort"],
                mib["NQA-MIB::nqaAdminParaDSField"],
                mib["NQA-MIB::nqaAdminParaVrfName"],
            ]
        ):
            # index = oid.split(".", 14)[-1]

            if index not in probes:
                continue
            if not target:
                self.logger.info("[%s] Probe without target", index)
                del probes[index]
                continue
            if target_port:
                target = f"{target}:{target_port}"
            if tos:
                probes[index]["tos"] = tos >> 2
            if vrf:
                probes[index]["vrf"] = vrf
            probes[index]["target"] = target

        return list(probes.values())
