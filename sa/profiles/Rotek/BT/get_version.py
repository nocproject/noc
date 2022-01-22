# ---------------------------------------------------------------------
# Rotek.BT.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Rotek.BT.get_version"
    cache = True
    interface = IGetVersion
    reuse_cli_session = False
    keep_cli_session = False

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
        sn = self.snmp.get("1.3.6.1.4.1.41752.5.15.1.10.0")
        if oid.startswith("BT"):
            o = oid.split(",", 1)[0].strip()
            if "REV2" in o:
                ro = o.split(" ")
                platform = "%s.%s" % (ro[0].strip(), ro[1].strip())
                if len(ro) == 4:
                    version = ro[3].strip()
                else:
                    version = ro[2].strip()
            else:
                platform = o.split(" ")[0].strip()
                version = o.split(" ")[1].strip()
            result = {
                "vendor": "Rotek",
                "version": version,
                "platform": platform,
                "attributes": {"Serial Number": sn},
            }
        else:
            platform = oid.split()[0].strip()
            version = oid.split()[1].strip()
            if "," in platform:
                platform = platform.split(",")[0]
            if platform == "RT-Pwr":
                # Version 1.4.0-b32048bc return RT-Pwr
                platform = "RT-Pwr-220-U"
            result = {
                "vendor": "Rotek",
                "version": version,
                "platform": platform,
                "attributes": {"Serial Number": sn},
            }
        return result
