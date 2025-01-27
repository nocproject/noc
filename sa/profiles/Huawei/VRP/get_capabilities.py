# ---------------------------------------------------------------------
# Huawei.VRP.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error, false_on_snmp_error
from noc.core.mib import mib
from noc.core.text import alnum_key


class Script(BaseScript):
    name = "Huawei.VRP.get_capabilities"

    CHECK_SNMP_GETNEXT = {
        "Huawei | MIB | ENTITY-EXTENT-MIB": mib["HUAWEI-ENTITY-EXTENT-MIB::hwEntityStateEntry"],
        "Huawei | OID | hwMemoryDevTable": mib["HUAWEI-DEVICE-MIB::hwMemoryDevEntry"],
        "Huawei | OID | hwCBQoSClassifierStatisticsTable": mib[
            "HUAWEI-CBQOS-MIB::hwCBQoSClassifierMatchedPackets"
        ],
        "Huawei | OID | hwCBQoSPolicyStatisticsClassifierTable": mib[
            "HUAWEI-CBQOS-MIB::hwCBQoSPolicyStatClassifierMatchedPassPackets"
        ],
        "Huawei | OID | hwOpticalModuleInfoTable": mib[
            "HUAWEI-ENTITY-EXTENT-MIB::hwEntityOpticalMode"
        ],
        "Huawei | OID | hwOpticalModuleInfoTable Lane": mib[
            "HUAWEI-ENTITY-EXTENT-MIB::hwEntityOpticalLaneBiasCurrent"
        ],
    }

    CHECK_SNMP_GET = {
        "Huawei | MIB | HUAWEI-CBQOS-MIB": mib["HUAWEI-CBQOS-MIB::hwCBQoSClassifierIndexNext", 0],
        "BRAS | PPPoE": "1.3.6.1.4.1.2011.5.2.1.14.1.2.0",
        "Network | DHCP": "1.3.6.1.4.1.2011.6.8.1.7.3.0",  # hwIPUsedTotalNum
    }
    rx_stp = re.compile(r"Protocol Status\s+:\s*Enabled")

    @false_on_cli_error
    def has_stp_cli(self):
        """
        Check box has STP enabled
        """
        try:
            r = self.cli("display stp global")
            return self.rx_stp.search(r) is not None
        except self.CLISyntaxError:
            try:
                r = self.cli("display stp | include isabled")
                return "Protocol Status" not in r
            except self.CLISyntaxError:
                r = self.cli("display stp")
                return "Protocol Status" not in r

    @false_on_cli_error
    def has_lldp_cli(self):
        """
        Check box has LLDP enabled
        """
        r = self.cli("display lldp local", cached=True)
        return (
            "LLDP is not enabled" not in r
            and "Global status of LLDP: Disable" not in r
            and "LLDP enable status:           disable" not in r
        )

    def has_lldp_snmp(self):
        """
        Check box has LLDP enabled
        """
        try:
            r = self.snmp.get("1.3.6.1.4.1.2011.5.25.134.1.1.1.0")
        except (self.snmp.TimeOutError, self.snmp.SNMPError):
            r = 0
        return bool(r)

    @false_on_cli_error
    def has_ndp_cli(self):
        """
        Check box has NDP enabled
        """
        r = self.cli("display ndp", cached=True)
        return "enabled" in r

    @false_on_cli_error
    def has_bfd_cli(self):
        """
        Check box has BFD enabled
        """
        r = self.cli("display bfd configuration all")
        return "Please enable BFD in global mode first" not in r

    @false_on_cli_error
    def has_udld_cli(self):
        """
        Check box has UDLD enabled
        """
        r = self.cli("display dldp")
        return "Global DLDP is not enabled" not in r and "DLDP global status : disable" not in r

    @false_on_cli_error
    def has_ldp_cli(self):
        """
        Check box has UDLD enabled
        """
        r = self.cli("display mpls ldp")
        return "Global LDP is not enabled" not in r or "Instance Status         : Active " not in r

    @false_on_snmp_error
    def has_ip_sla_responder_snmp(self):
        r = self.snmp.get(mib["NQA-MIB::nqaSupportServerType", 0])
        return r != 2

    @false_on_snmp_error
    def get_ip_sla_probes_snmp(self):
        r = self.snmp.count(mib["NQA-MIB::nqaAdminCtrlStatus"])
        return r

    @false_on_cli_error
    def has_stack(self):
        """
        Check stack members
        :return:
        """
        out = self.cli("display stack")
        if "device is not in stacking" in out:
            return []
        r = self.profile.parse_table(out, part_name="stack")
        return [ll[0] for ll in r["stack"]["table"]] if "table" in r["stack"] else []

    def get_inventory(self):
        """Collect slot, modules and sfp on ENTITY-MIB"""
        slots, modules, ports = set(), set(), set()
        if not self.has_snmp():
            return slots, modules, ports
        max_slots, s_pos = 0, 0
        if self.is_me60:
            # ME60-X16A, ME60-X8A, ME60-X16, ME60-X8, ME60-X3 filter LPU
            max_slots = int(self.version["platform"].strip("A")[6:])
        for oid, entity_class in self.snmp.getnext(
            mib["ENTITY-MIB::entPhysicalClass"],
            bulk=False,
        ):
            _, index = oid.rsplit(".", 1)
            if entity_class == 9:
                modules.add(index)
                if max_slots:
                    slots.add(s_pos)
            elif entity_class == 10:
                ports.add(index)
            elif entity_class == 5:
                s_pos = index
        transceivers = set()
        if ports:
            r = self.snmp.get_chunked(
                [mib["HUAWEI-ENTITY-EXTENT-MIB::hwEntityBoardType", x] for x in sorted(ports)],
            )
            for oid, v in r.items():
                if not v.strip():
                    continue
                transceivers.add(oid.rsplit(".", 1)[-1])
        if slots:
            r = self.snmp.get_chunked(
                [mib["ENTITY-MIB::entPhysicalParentRelPos", x] for x in sorted(slots)],
            )
            slots = [str(x) for x in set(r.values()) if x <= max_slots]
        return slots, modules, transceivers

    @false_on_cli_error
    def has_lacp_cli(self):
        """
        Check stack members
        :return:
        """
        r = self.cli("display lacp statistics eth-trunk")
        return r

    def execute_platform_cli(self, caps):
        if self.has_ndp_cli():
            caps["Huawei | NDP"] = True
        s = self.has_stack()
        slots, modules, transceivers = self.get_inventory()
        if s:
            caps["Stack | Members"] = len(s) if len(s) != 1 else 0
            caps["Stack | Member Ids"] = " | ".join(s)
        if slots:
            caps["Slot | Members"] = len(slots) if len(slots) != 1 else 0
            caps["Slot | Member Ids"] = " | ".join(slots)
        if modules:
            caps["Huawei | SNMP | ModuleIndex"] = " | ".join(modules)
        if transceivers:
            caps["Huawei | SNMP | DOM Indexes"] = " | ".join(sorted(transceivers, key=alnum_key))
        # Check IP SLA status
        # sla_v = self.snmp.get(mib["NQA-MIB::nqaEnable", 0])
        # if sla_v:
        # IP SLA responder
        if self.has_ip_sla_responder_snmp():
            caps["Huawei | NQA | Responder"] = True
        # IP SLA Probes
        np = self.get_ip_sla_probes_snmp()
        if np:
            caps["Huawei | NQA | Probes"] = np

    def execute_platform_snmp(self, caps):
        slots, modules, transceivers = self.get_inventory()
        if slots:
            caps["Slot | Members"] = len(slots) if len(slots) != 1 else 0
            caps["Slot | Member Ids"] = " | ".join(slots)
        if modules:
            caps["Huawei | SNMP | ModuleIndex"] = " | ".join(modules)
        if transceivers:
            caps["Huawei | SNMP | DOM Indexes"] = " | ".join(sorted(transceivers, key=alnum_key))
        # Check IP SLA status
        # sla_v = self.snmp.get(mib["NQA-MIB::nqaEnable", 0])
        # IP SLA Probes
        np = self.get_ip_sla_probes_snmp()
        if np:
            caps["Huawei | NQA | Probes"] = np
            # IP SLA responder
            # if self.has_ip_sla_responder_snmp():
            #     caps["Huawei | NQA | Responder"] = True
