# ---------------------------------------------------------------------
# BDCOM.xPON.get_cpe
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetcpe import IGetCPE
from noc.core.text import parse_table
from noc.core.validators import is_int
from noc.core.mac import MAC


class Script(BaseScript):
    name = "BDCOM.xPON.get_cpe"
    interface = IGetCPE
    TIMEOUT = 600
    always_prefer = "S"

    rx_gpon_image_iface = re.compile(
        r"^Image information of (?P<pon_id>\S+):\s*\n",
        re.MULTILINE,
    )
    rx_gpon_image_version = re.compile(
        r"^\s+Image#\d+\s+(?P<version>\S+)\s+valid\s+active\s+committed",
        re.MULTILINE,
    )
    rx_epon_sw_version = re.compile(
        r"^(?P<onu_id>EPON\d+/\d+:\d+)\s+(?P<version>\S+)\s*\n",
        re.MULTILINE,
    )
    rx_onu_model_id = re.compile(r"^ONU MODEL ID\s+: (?P<model>\S{4})\s*\n", re.MULTILINE)
    rx_onu_ext_id = re.compile(r"^ONU EXT MODEL ID\s+: (?P<ext_model>\S+)\s*\n", re.MULTILINE)
    rx_onu_sw = re.compile(r"^Software Version\s+:\s+(?P<version>\S+)\s*\n", re.MULTILINE)
    rx_onu_hw = re.compile(r"^Hardware Version\s+: (?P<revision>\S+)\s*\n", re.MULTILINE)

    CLI_STATUS_MAP = {
        "auto-configured": "active",
        "auto-configuring": "provisioning",
        "authenticated": "active",
        "active": "active",
    }
    SNMP_STATUS_MAP = {
        "0": "active",  # authenticated
        "1": "active",  # registered
        "2": "inactive",  # deregistered
        "3": "active",  # auto_config
        "4": "inactive",  # lost
        "5": "other",  # standby
    }
    ONU_MAP = {
        "BDCM": {
            "3024": "P1004B",
            "3022": "P1501B",
            "151C": "P1501C",
            "1004": "P1004T",
            "104C": "P1004C",
            "1154": "GP1702-1Gv2",
            "6014": "P1501DT",
            "6032": "P1501DS",
        },
        "FORA": {
            "0311": "NA-1001B",
            "101C": "NA-1001C",
            "100D": "NA-1001D",
        },
        "FGXP": {
            "2001": "G2001R",
        },
        "GEAR": {
            "1004": "P1004T",
        },
        "MONU": {
            "H323": "RTKG",
        },
        "NGPN": {
            "NG02": "NGN-02E",
        },
        "PCTL": {  # Picotel
            "G100": "GE100",
            "NG02": "GE100N",
        },
        "PICO": {  # Picotel
            "100N": "Ge-100N",
        },
        "SNR": {
            "SNR-ONU-EPON-1G-": "SNR-ONU-EPON-1G-mini",
        },
        "TPLK": {
            "110": "TL-EP110",
        },
        "ZTE": {
            "ONU-": "ONU-501",
        },
    }

    def get_onu_model(self, vendor, model):
        if vendor in self.ONU_MAP:
            return self.ONU_MAP.get(vendor).get(model, model)
        return model

    def execute_cli(self, **kwargs):
        r = {}
        if self.is_gpon:
            v = self.cli("show gpon onu-information", cached=True)
            for i in parse_table(v):
                onu = {
                    "id": i[0],
                    "global_id": i[3],
                    "serial": i[3],
                    "type": "ont",
                    "interface": i[0],
                }
                onu["vendor"] = i[1]
                if i[2] != "N/A":
                    onu["model"] = self.get_onu_model(i[1], i[2])
                onu["status"] = self.CLI_STATUS_MAP.get(i[5], "inactive")
                r[onu["id"]] = dict(onu)
            v = self.cli("show gpon active-onu")
            for i in parse_table(v):
                r[i[0]]["distance"] = int(float(i[5]))
            v = self.cli("show gpon onu-description")
            for i in parse_table(v):
                if i[1] == "N/A":
                    continue
                r[i[0]]["description"] = i[1]
            v = self.cli("show gpon onu-image-information")
            for i in v.split("\n\n"):
                onu_id = self.rx_gpon_image_iface.search(i)
                version = self.rx_gpon_image_version.search(i)
                if onu_id is None or version is None:
                    continue
                r[onu_id.group("pon_id")]["version"] = version.group("version")
        else:
            v = self.cli("show epon onu-information", cached=True)
            for i in parse_table(v):
                onu = {
                    "id": i[0],
                    "global_id": i[3],
                    "type": "ont",
                    "interface": i[0],
                }
                if i[1] != "----":
                    onu["vendor"] = i[1]
                    if "/" in i[2]:
                        i[2] = i[2].split("/")[1]
                    onu["model"] = self.get_onu_model(i[1], i[2])
                if i[4] != "N/A":
                    onu["description"] = i[4]
                onu["status"] = self.CLI_STATUS_MAP.get(i[6], "inactive")
                r[onu["id"]] = dict(onu)
            v = self.cli("show epon active-onu")
            for i in parse_table(v):
                if is_int(i[4]):
                    r[i[0]]["distance"] = i[4]
            v = self.cli("show epon onu-software-version")
            for i in parse_table(v):
                if i[0].startswith("EPON"):
                    r[i[0]]["version"] = i[1]

        return sorted(r.values(), key=lambda x: x["id"])

    def execute_snmp(self, **kwargs):
        r = {}
        if self.is_gpon:
            # NMS-GPON-MIB::onuSerialNum
            for oid, value in self.snmp.getnext("1.3.6.1.4.1.3320.10.3.1.1.4"):
                ifindex = int(oid.split(".")[-1])
                r[ifindex] = {
                    "global_id": value,
                    "serial": value,
                    "type": "ont",
                }
            # IF-MIB::ifDescr
            for oid, value in self.snmp.getnext("1.3.6.1.2.1.2.2.1.2"):
                ifindex = int(oid.split(".")[-1])
                if ifindex in r:
                    r[ifindex]["id"] = value
                    r[ifindex]["interface"] = value
            # NMS-GPON-MIB::onuVendorID
            for oid, value in self.snmp.getnext("1.3.6.1.4.1.3320.10.3.1.1.2"):
                ifindex = int(oid.split(".")[-1])
                if ifindex in r:
                    if value != "":
                        r[ifindex]["vendor"] = value
                    else:  # hack for deregistered ONU
                        r[ifindex]["vendor"] = r[ifindex]["global_id"].split(".")[-1]
            # NMS-GPON-MIB::onuVersion
            for oid, value in self.snmp.getnext("1.3.6.1.4.1.3320.10.3.1.1.3"):
                ifindex = int(oid.split(".")[-1])
                value = value.rstrip().rstrip("\x00")
                if ifindex in r and value != "":
                    r[ifindex]["revision"] = value
            # NMS-GPON-MIB::onuOperationalState - enable(1), disable(2)
            for oid, value in self.snmp.getnext("1.3.6.1.4.1.3320.10.3.1.1.8"):
                ifindex = int(oid.split(".")[-1])
                value = int(value)
                if ifindex in r:
                    r[ifindex]["status"] = "active" if value == 1 else "inactive"
            # NMS-GPON-MIB::onuEquipmentID
            for oid, value in self.snmp.getnext("1.3.6.1.4.1.3320.10.3.1.1.9"):
                ifindex = int(oid.split(".")[-1])
                if ifindex in r and value != "":
                    r[ifindex]["model"] = value
            # NMS-GPON-MIB::onuImageInstance0Version ...
            for ifindex, value, valid, active, commited in self.snmp.get_tables(
                [
                    "1.3.6.1.4.1.3320.10.3.1.1.20",
                    "1.3.6.1.4.1.3320.10.3.1.1.21",
                    "1.3.6.1.4.1.3320.10.3.1.1.22",
                    "1.3.6.1.4.1.3320.10.3.1.1.23",
                ]
            ):
                ifindex = int(ifindex)
                value = value.rstrip().rstrip("\x00")
                if (
                    ifindex in r
                    and value != ""
                    and int(valid) == 1
                    and int(active) == 1
                    and int(commited) == 1
                ):
                    r[ifindex]["version"] = value
            # NMS-GPON-MIB::onuImageInstance1Version ...
            for ifindex, value, valid, active, commited in self.snmp.get_tables(
                [
                    "1.3.6.1.4.1.3320.10.3.1.1.24",
                    "1.3.6.1.4.1.3320.10.3.1.1.25",
                    "1.3.6.1.4.1.3320.10.3.1.1.26",
                    "1.3.6.1.4.1.3320.10.3.1.1.27",
                ]
            ):
                ifindex = int(ifindex)
                value = value.rstrip().rstrip("\x00")
                if (
                    ifindex in r
                    and value != ""
                    and int(valid) == 1
                    and int(active) == 1
                    and int(commited) == 1
                ):
                    r[ifindex]["version"] = value
            # NMS-EPON-MIB::onuDistance
            for oid, value in self.snmp.getnext("1.3.6.1.4.1.3320.10.3.1.1.33"):
                ifindex = int(oid.split(".")[-1])
                value = int(value)
                if ifindex in r and value != 0:
                    r[ifindex]["distance"] = value // 10
        else:
            # NMS-EPON-MIB::onuID
            for oid, value in self.snmp.getnext("1.3.6.1.4.1.3320.101.10.1.1.3"):
                ifindex = int(oid.split(".")[-1])
                r[ifindex] = {
                    "global_id": MAC(value),
                    "mac": MAC(value),
                    "type": "ont",
                }
            # IF-MIB::ifDescr
            for oid, value in self.snmp.getnext("1.3.6.1.2.1.2.2.1.2"):
                ifindex = int(oid.split(".")[-1])
                if ifindex in r:
                    r[ifindex]["id"] = value
                    r[ifindex]["interface"] = value
            # NMS-EPON-MIB::onuVendorID
            for oid, value in self.snmp.getnext("1.3.6.1.4.1.3320.101.10.1.1.1"):
                ifindex = int(oid.split(".")[-1])
                if ifindex in r and value != "----":
                    r[ifindex]["vendor"] = value
            # NMS-EPON-MIB::onuModuleID
            for oid, value in self.snmp.getnext("1.3.6.1.4.1.3320.101.10.1.1.2"):
                ifindex = int(oid.split(".")[-1])
                if ifindex in r and value != "----":
                    value = self.get_onu_model(r[ifindex]["vendor"], value)
                    r[ifindex]["model"] = value
            # NMS-EPON-MIB::onuHardwareVersion
            for oid, value in self.snmp.getnext("1.3.6.1.4.1.3320.101.10.1.1.4"):
                ifindex = int(oid.split(".")[-1])
                value = value.rstrip("\x00")
                if ifindex in r and value != "":
                    r[ifindex]["revision"] = value
            # NMS-EPON-MIB::onuSoftwareVersion
            for oid, value in self.snmp.getnext("1.3.6.1.4.1.3320.101.10.1.1.5"):
                ifindex = int(oid.split(".")[-1])
                value = value.rstrip("\x00")
                if ifindex in r and value != "":
                    r[ifindex]["version"] = value
            # NMS-EPON-MIB::onuStatus
            for oid, value in self.snmp.getnext("1.3.6.1.4.1.3320.101.10.1.1.26"):
                ifindex = int(oid.split(".")[-1])
                value = int(value)
                if ifindex in r:
                    r[ifindex]["status"] = self.SNMP_STATUS_MAP.get(value, "inactive")
            # NMS-EPON-MIB::onuDistance
            for oid, value in self.snmp.getnext("1.3.6.1.4.1.3320.101.10.1.1.27"):
                ifindex = int(oid.split(".")[-1])
                value = int(value)
                if ifindex in r and value != 0:
                    r[ifindex]["distance"] = value
            # NMS-EPON-MIB::onuExtModelID
            for oid, value in self.snmp.getnext("1.3.6.1.4.1.3320.101.10.1.1.85"):
                ifindex = int(oid.split(".")[-1])
                if ifindex in r and r[ifindex].get("vendor") is not None and value != "":
                    value = self.get_onu_model(r[ifindex]["vendor"], value)
                    r[ifindex]["model"] = value
        return list(r.values())
