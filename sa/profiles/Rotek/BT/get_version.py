# ---------------------------------------------------------------------
# Rotek.BT.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from typing import Tuple, Optional

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Rotek.BT.get_version"
    cache = True
    interface = IGetVersion
    reuse_cli_session = False
    keep_cli_session = False

    rx_bt_platform = re.compile(
        r"BT-?(?P<platform>\d+)\(?(?P<hw_ver>v\d)?\s?(?P<rev>rev\d)?\)?"
        r"\s+v?(?P<version>\d+\.\d+)[\s,].*",
        re.IGNORECASE,
    )

    def normalize_platform(self, oid: str) -> Tuple[str, Optional[str], Optional[str]]:
        """
        Normalize platform name from OID String

        # BT6037(V1 REV2)  v1.23, ZAO "NPK RoTeK"
        # BT6037(V1 REV2)  v1.22, ZAO "NPK RoTeK"
        # BT-6037v1rev3 3.0  KN-03-00082
        # BT6037(V1) v1.16, ZAO "NPK RoTeK"
        # RT-Pwr-220-U,4250L 4.3.0-d883291  5312480
        # RT-Pwr,4250LSR 1.4.0-b32048bc  5331034

        :param oid:
        :return: Platform and Version

        """
        platform, version, hw_ver = None, None, None
        match = self.rx_bt_platform.match(oid)
        if match:
            platform, _, hw_ver, version = match.groups()
            platform = f"BT-{platform}"
        elif oid.startswith("RT"):
            platform, version, *_ = oid.split()
            if "," in platform:
                _, platform = platform.split(",")
            platform = f"RT-{platform}"
        if not platform:
            raise self.NotSupportedError("Not supported controller")
        return platform, version, hw_ver

    def execute_cli(self, **kwargs):
        v = self.http.get("/info.cgi?_", json=True, cached=True, eof_mark=b"}")
        platform = v["model"]
        if "," in platform:
            platform = platform.split(",")[0]
        if platform == "RT-Pwr":
            # Version 1.4.0-b32048bc return RT-Pwr
            platform = "RT-Pwr-220-U"
        return {
            "vendor": "Rotek",
            "version": v["fwversion"],
            "platform": platform,
            "attributes": {"Serial Number": v["serno"]},
        }

    def execute_snmp(self):
        oid = self.snmp.get("1.3.6.1.2.1.1.1.0")
        platform, version, hw_rev = self.normalize_platform(oid)
        r = {
            "vendor": "Rotek",
            "version": version or "",
            "platform": platform,
            "attributes": {},
        }
        if hw_rev:
            r["attributes"]["HW version"] = hw_rev.upper()
        sn_oid = "1.3.6.1.4.1.41752.5.15.1.10.0"
        if platform == "RT-4250LSR":
            sn_oid = "1.3.6.1.4.1.41752.911.10.1.11.0"
        sn = self.snmp.get(sn_oid)
        if sn:
            r["attributes"]["Serial Number"] = sn
        return r
