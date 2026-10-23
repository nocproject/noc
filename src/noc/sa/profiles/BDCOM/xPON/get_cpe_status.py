# ---------------------------------------------------------------------
# BDCOM.xPON.get_cpe_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetcpestatus import IGetCPEStatus
from noc.core.text import parse_table
from noc.core.mac import MAC


class Script(BaseScript):
    name = "BDCOM.xPON.get_cpe_status"
    interface = IGetCPEStatus
    always_prefer = "S"

    CLI_STATUS_MAP = {
        "auto-configured": True,
        "auto-configuring": False,
        "authenticated": True,
        "active": True,
    }
    SNMP_STATUS_MAP = {
        0: True,  # authenticated
        1: True,  # registered
        2: False,  # deregistered
        3: True,  # auto_config
        4: False,  # lost
        5: True,  # standby
    }

    def execute_cli(self, **kwargs):
        r = []
        if self.is_gpon:
            v = self.cli("show gpon onu-information", cached=True)
            for i in parse_table(v):
                onu = {
                    "interface": i[0],
                    "local_id": i[0],
                    "global_id": i[3],
                }
                onu["oper_status"] = self.CLI_STATUS_MAP.get(i[5], False)
                r.append(onu)
        else:
            v = self.cli("show epon onu-information", cached=True)
            for i in parse_table(v):
                onu = {
                    "interface": i[0],
                    "local_id": i[0],
                    "global_id": i[3],
                }
                onu["oper_status"] = self.CLI_STATUS_MAP.get(i[6], False)
                r.append(onu)
        return r

    def execute_snmp(self, **kwargs):
        r = {}
        if self.is_gpon:
            # NMS-GPON-MIB::onuSerialNum
            for oid, value in self.snmp.getnext("1.3.6.1.4.1.3320.10.3.1.1.4"):
                ifindex = int(oid.split(".")[-1])
                r[ifindex] = {
                    "global_id": value,
                }
            # IF-MIB::ifDescr
            for oid, value in self.snmp.getnext("1.3.6.1.2.1.2.2.1.2"):
                ifindex = int(oid.split(".")[-1])
                if ifindex in r:
                    r[ifindex]["local_id"] = value
                    r[ifindex]["interface"] = value
            # NMS-GPON-MIB::onuOperationalState - enable(1), disable(2)
            for oid, value in self.snmp.getnext("1.3.6.1.4.1.3320.10.3.1.1.8"):
                ifindex = int(oid.split(".")[-1])
                value = int(value)
                if ifindex in r:
                    r[ifindex]["oper_status"] = value == 1
        else:
            # NMS-EPON-MIB::onuID
            for oid, value in self.snmp.getnext("1.3.6.1.4.1.3320.101.10.1.1.3"):
                ifindex = int(oid.split(".")[-1])
                r[ifindex] = {
                    "global_id": MAC(value),
                }
            # IF-MIB::ifDescr
            for oid, value in self.snmp.getnext("1.3.6.1.2.1.2.2.1.2"):
                ifindex = int(oid.split(".")[-1])
                if ifindex in r:
                    r[ifindex]["local_id"] = value
                    r[ifindex]["interface"] = value
            # NMS-EPON-MIB::onuStatus
            for oid, value in self.snmp.getnext("1.3.6.1.4.1.3320.101.10.1.1.26"):
                ifindex = int(oid.split(".")[-1])
                value = int(value)
                if ifindex in r:
                    r[ifindex]["oper_status"] = self.SNMP_STATUS_MAP.get(value, False)

        return list(r.values())
