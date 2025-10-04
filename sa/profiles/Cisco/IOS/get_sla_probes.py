# ---------------------------------------------------------------------
# Cisco.IOS.get_sla_probes
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from collections import defaultdict

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetslaprobes import IGetSLAProbes
from noc.core.mib import mib
from noc.core.snmp.render import render_bin


class Script(BaseScript):
    name = "Cisco.IOS.get_sla_probes"
    interface = IGetSLAProbes

    CAP_SLA_SYNTAX = "Cisco | IOS | Syntax | IP SLA"

    SYNTAX_SLA_CONFIG = ["show ip sla config", "show ip sla monitor config"]

    rx_entry = re.compile(
        r"Entry number: (?P<name>\d+)\s*\n", re.MULTILINE | re.DOTALL | re.IGNORECASE
    )

    rx_type = re.compile(
        r"Type of operation to perform:\s+(?P<type>\S+)", re.MULTILINE | re.IGNORECASE
    )

    rx_target = re.compile(r"Target address/Source \S+: (?P<target>[^/]+)/", re.MULTILINE)

    rx_target1 = re.compile(r"Target address: (?P<target>\S+)", re.MULTILINE)

    rx_target_port = re.compile(r"Target port/Source port\s*: (?P<target>[^/]+)/", re.MULTILINE)

    rx_tag = re.compile(r"Tag: *(?P<tag>[^\n]+)\n", re.MULTILINE)

    rx_owner = re.compile(r"Owner: *(?P<owner>[^\n]+)\n", re.MULTILINE)

    rx_tos = re.compile(r"Type Of Service parameter: *(?P<tos>[^\n]+)\n", re.MULTILINE)

    rx_vrf = re.compile(r"Vrf Name: *(?P<vrf>[^\n]+)\n", re.MULTILINE)

    rx_status = re.compile(
        r"Status of entry \(SNMP RowStatus\)\s*: *(?P<status>[^\n]+)\n", re.MULTILINE
    )

    # IOS to interface type conversion
    # @todo: Add other types
    TEST_TYPES = {
        "icmp-echo": "icmp-echo",
        "path-jitter": "path-jitter",
        "udp-jitter": "udp-jitter",
        "icmp-jitter": "icmp-echo",
        "echo": "icmp-echo",
        "udp-echo": "udp-echo",
        "tcp-connect": "tcp-connect",
    }

    def execute_cli(self, **kwargs):
        if not self.has_capability(self.CAP_SLA_SYNTAX, allow_zero=True):
            return []
        cfg = self.cli(self.SYNTAX_SLA_CONFIG[self.capabilities[self.CAP_SLA_SYNTAX]])
        r = []
        for name, config in self.iter_pairs(self.rx_entry.split(cfg), offset=1):
            match = self.rx_type.search(config)
            if not match:
                self.logger.error("Cannot find type for IP SLA probe %s. Ignoring", name)
                continue
            type = match.group("type")
            match = self.rx_target.search(config)
            if not match:
                match = self.rx_target1.search(config)
                if not match:
                    self.logger.error("Cannot find target for IP SLA probe %s. Ignoring", name)
            if type not in self.TEST_TYPES:
                self.logger.error("Unknown test type %s for IP SLA probe %s. Ignoring", type, name)
            type = self.TEST_TYPES[type]
            target = match.group("target")
            match = self.rx_target_port.search(config)
            if match and match.group("target") != "0":
                target += f":{match.group('target').strip()}"
            match = self.rx_owner.search(config)
            group = ""
            if match:
                group = match.group("owner").strip()
            status = True
            match = self.rx_status.search(config)
            self.logger.debug("[%s:%s] Status: %s", type, name, match)
            if match:
                status = match.group("status").strip() == "Active"
            r += [{"name": name, "group": group, "type": type, "target": target, "status": status}]
            match = self.rx_tos.search(config)
            if match:
                r[-1]["tos"] = int(match.group("tos").strip(), 16) >> 2
            match = self.rx_vrf.search(config)
            if match:
                r[-1]["vrf"] = match.group("vrf").strip()
            match = self.rx_tag.search(config)
            if match:
                tag = match.group("tag").strip()
                if tag:
                    r[-1]["description"] = tag
        return r

    probes_snmp_type_map = {
        1: "icmp-echo",
        9: "udp-jitter",
    }

    def execute_snmp(self, **kwargs):
        probes = defaultdict(dict)
        for index, owner, tag, rtt_type, status in self.snmp.get_tables(
            [
                mib["CISCO-RTTMON-MIB::rttMonCtrlAdminOwner"],
                mib["CISCO-RTTMON-MIB::rttMonCtrlAdminTag"],
                mib["CISCO-RTTMON-MIB::rttMonCtrlAdminRttType"],
                mib["CISCO-RTTMON-MIB::rttMonCtrlAdminStatus"],
                # mib["CISCO-RTTMON-MIB::rttMonCtrlAdminGroupName"],
            ],
            bulk=False,
        ):
            if rtt_type not in self.probes_snmp_type_map:
                self.logger.info("Unknown Probe type: %s. Skipping...", rtt_type)
                continue
            index = str(index)
            probes[index] = {
                "name": index,
                "group": owner,
                "status": status,
                "type": self.probes_snmp_type_map[rtt_type],
            }
            if tag:
                probes[index]["tags"] = [f"noc::sla::tag::{tag}"]
        # Getting target
        for index, target, target_port, tos, vrf in self.snmp.get_tables(
            [
                mib["CISCO-RTTMON-MIB::rttMonEchoAdminTargetAddress"],
                mib["CISCO-RTTMON-MIB::rttMonEchoAdminTargetPort"],
                mib["CISCO-RTTMON-MIB::rttMonEchoAdminTOS"],
                mib["CISCO-RTTMON-MIB::rttMonEchoAdminVrfName"],
            ],
            display_hints={mib["CISCO-RTTMON-MIB::rttMonEchoAdminTargetAddress"]: render_bin},
        ):
            # key = oid.rsplit(".", 1)[-1]
            if index not in probes:
                self.logger.debug("[%s] Probe not in probes config. Skipping target", index)
                continue
            target = ".".join(str(int(x)) for x in target)
            if target_port:
                target += f":{target_port}"
            probes[index]["target"] = target
            if vrf:
                probes[index]["vrf"] = vrf
            if tos:
                probes[index]["tos"] = tos >> 2
        # Getting Schedule
        for oid, ptime in self.snmp.getnext(
            mib["CISCO-RTTMON-MIB::rttMonScheduleAdminRttStartTime"]
        ):
            key = oid.rsplit(".", 1)[-1]
            if key in probes and not ptime:
                self.logger.debug("[%s] Probe not schedules. Set status to False", key)
                probes[key]["status"] = False
        return list(probes.values())
