# ---------------------------------------------------------------------
# BDCOM.xPON.get_cpe
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetcpe import IGetCPE
from noc.sa.interfaces.base import MACAddressParameter


class Script(BaseScript):
    name = "BDCOM.xPON.get_cpe"
    interface = IGetCPE

    splitter = re.compile(r"\s*-+\n")

    status_map = {
        "auto-configured": "active",
        "auto-configuring": "active",
        "authenticated": "active",
        "lost": "inactive",
        "deregistered": "inactive",
    }

    # EPON port can contain maximum 64 ONU
    ifname_validator = re.compile(r"^EPON\d+/\d+:\d{1,2}$")
    ifname_match = re.compile(r"^(?P<ifname>EPON\d+/\d+:\d{1,2})")
    status_match = re.compile(
        r"^(?P<status>auto-configured|auto-configuring|authenticated|lost|deregistered)"
    )

    def get_onu_status(self, raw_status):
        m = self.status_match.match(raw_status)
        if m:
            status = m["status"]
        else:
            self.logger.info("Unknown ONU status '%s'. Fallback to oper_state 'down'", raw_status)
            return "inactive"

        return self.status_map[status]

    def get_onu_local_id(self, raw_id):
        m = self.ifname_match.match(raw_id)
        if m:
            ifname = m["ifname"]
        else:
            self.logger.info("Unknown ONU ifname '%s'. Return raw value", raw_id)
            return raw_id

        return ifname

    def execute_cli(self, **kwargs):
        r = []
        v = self.cli("show epon onu-information")
        for table in v.split("\n\n"):
            parts = self.splitter.split(table)
            for p in parts[1:]:
                for onu in p.split("\n"):
                    line = onu.split()
                    if len(line) >= 8 or self.ifname_validator.match(line[0]):
                        onu_id = line[0]
                        onu_vendor = line[1]
                        onu_model = line[2]
                        onu_mac = MACAddressParameter().clean(line[3])
                        onu_status = self.get_onu_status(line[6])
                    else:
                        # Sometimes first fields overlaps on some firmware version
                        # IntfName   VendorID  ModelID    MAC Address    Description                     BindType  Status          Dereg Reason
                        # ---------- --------- ---------- -------------- ------------------------------- --------- --------------- -----------------
                        # EPON0/13:9 VSOL      D401       006d.61d4.6bf8 N/A                             static    auto-configured N/A
                        # EPON0/13:10xPON      101Z       e0e8.e61f.0759 N/A                             static    auto-configured N/A
                        #
                        # Or last fields
                        # EPON0/3:38 VSOL      D401      006d.61d3.ee10 N/A             static    auto-configuringN/A

                        onu_id = self.get_onu_local_id(line[0])
                        onu_vendor = line[0].replace(onu_id, "")
                        onu_model = line[1]
                        onu_mac = MACAddressParameter().clean(line[2])
                        onu_status = self.get_onu_status(line[5])

                    r.append(
                        {
                            "vendor": onu_vendor,
                            "model": onu_model,
                            "mac": onu_mac,
                            "status": onu_status,
                            "id": onu_id,
                            "global_id": onu_mac,
                            "type": "ont",
                            "serial": onu_mac,
                            "description": "",
                        }
                    )

        return r
