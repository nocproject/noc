# ----------------------------------------------------------------------
# Huawei.MA5600T.gpon_ports
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.script.oidrules.oid import OIDRule
from noc.core.mib import mib


class GponPortsRule(OIDRule):
    name = "gponports"

    METRIC_MAP = {
        "Interface | Load | In": "HUAWEI-XPON-MIB::hwGponOltEthernetStatisticReceivedBytes",
        "Interface | Load | Out": "HUAWEI-XPON-MIB::hwGponOltEthernetStatisticSendBytes",
        "Interface | Packets | In": "HUAWEI-XPON-MIB::hwGponOltEthernetStatisticReceivedPakts",
        "Interface | Packets | Out": "HUAWEI-XPON-MIB::hwGponOltEthernetStatisticSendPakts",
        "Interface | Discards | Out": "HUAWEI-XPON-MIB::hwGponOltEthernetStatisticDropPakts",
        "Interface | Errors | In": "HUAWEI-XPON-MIB::hwGponOltEthernetStatisticReceivedCRCErrPakts",
    }

    def iter_oids(self, script, metric):
        if not hasattr(script, "_iface_snmp_type"):
            script._iface_snmp_type = {}
            for oid, snmp_type in script.snmp.getnext(mib["IF-MIB::ifType"]):
                if snmp_type == 250:
                    # gpon
                    _, ifindex = oid.rsplit(".", 1)
                    script._iface_snmp_type[int(ifindex)] = ""
        oid = None
        if metric.ifindex in script._iface_snmp_type and metric.metric in self.METRIC_MAP:
            # "HUAWEI-XPON-MIB::hwGponOltEthernetStatisticReceivedBytes"
            oid = mib[
                self.expand(
                    self.oid,
                    {"oid_prifix": self.METRIC_MAP[metric.metric], "ifindex": metric.ifindex},
                )
            ]
        if oid:
            yield oid, self.type, self.scale, self.units, metric.labels
