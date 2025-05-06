# ---------------------------------------------------------------------
# Maipu.OS.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

import re
# NOC modules
from noc.sa.profiles.Generic.get_inventory import Script as BaseScript


class Script(BaseScript):
    name = "Maipu.OS.get_inventory"

    rx_optical_info = re.compile(
        r"(?P<iface>\S+)\s+optical information$"
        r".*"
        r"\s+Vendor Name\s+:\s+(?P<vendor>[^ ,]+)$"
        r"\s+Part Number\s+:\s+(?P<part_no>[^ ,]+)$"
        r"\s+Revision Number\s+:\s*$"
        r"\s+Serial Number\s+:\s+(?P<serial>[^ ,]+)",
        re.MULTILINE | re.DOTALL | re.IGNORECASE
    )

    def execute_cli(self):
        v = self.scripts.get_version()
        serial = self.capabilities.get("Chassis | Serial Number")
        revision = self.capabilities.get("Chassis | HW Version")
        res = [
            {
                "type": "CHASSIS",
                "vendor": v["vendor"],
                "part_no": [v["platform"]],
                "number": 0,
                "serial": serial,
                "revision": revision,
            }
        ]

        # show system power
        #idata-stand01-nss3530#show system module brief
        #
        #module information display:
        #
        #Module          Online State          Name                            SN                               userSN
        #----------------------------------------------------------------------------------------------------------------------
        #Mpu 0           online Start Ok       NSS3530-30TXF(V1)               23006706000128
        #Power 1         online Normal         AD75M-HS0N(V1)                  23165720000586

        v = self.cli("show system module brief")
        for m in self.profile.rx_module_info.finditer(v):
            m_name = m["module_name"]

            # Mpu 0 already in chasssis field
            if m_name == "Mpu 0":
                continue

            r = {
                "vendor": "Maipu",
                "part_no": [m["part_no"]],
                "serial": m["serial"],
            }

            if m_name.startswith("Power"):
                r["type"] = "PSU"
                m_name_parts = m_name.split()
                if len(m_name_parts) != 2:
                    continue
                r["number"] = m_name_parts[1]
                res.append(r)

        v = self.cli("show optical all detail")
        for m in self.rx_optical_info.finditer(v):
            r = {
                "type": "XCVR",
                "vendor": m["vendor"],
                "part_no": m["part_no"],
                "serial": m["serial"],
            }

            # gigabitethernet0/1
            # tengigabitethernet0/25
            iface_parts = m["iface"].split("/")
            if len(iface_parts) != 2:
                self.logger.debug("[%s] has not contain 2 parts", m["iface"])
                continue

            r["number"] = iface_parts[1]

            res.append(r)

        return res