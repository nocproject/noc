# ---------------------------------------------------------------------
# Telecom.CPE.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2023-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from typing import Tuple, Optional

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Telecom.CPE.get_version"
    cache = True
    interface = IGetVersion
    rx_bt_param = re.compile(
        r"^.* model: NPOTELECOM (?P<platform>.+) kernel: (?P<kernel>.+) software: (?P<version>.*) machine:.*",
        re.IGNORECASE,
    )

    def normalize_param(self, oid: str) -> Tuple[str, Optional[str], Optional[dict]]:
        """
        Normalize platform name from OID String

        "sysname: Linux model: NPOTELECOM CPE-WIFI-2G kernel: 5.4.238 software: OpenWrt 21.02.7 r16847-f8282da11e machine: mips manufacturer: NPOTELECOM"
        platform: NPOTELECOM CPE-WIFI-2G
        version: OpenWrt 21.02.7 r16847-f8282da11e
        attributes:
            kernel: 5.4.238

        :param oid:
        :return: platform, version, attributes
        """
        platform, version, attributes = None, None, {}
        match = self.rx_bt_param.match(oid)
        if match:
            platform, kernel, version = match.groups()
            if kernel:
                attributes["kernel"] = kernel
        return platform, version, attributes

    def execute_snmp(self):
        oid = self.snmp.get("1.3.6.1.2.1.1.1.0")
        platform, version, attributes = self.normalize_param(oid)
        r = {
            "vendor": "Telecom",
            "version": version or "",
            "platform": platform or "",
            "attributes": attributes or "",
        }
        return r
