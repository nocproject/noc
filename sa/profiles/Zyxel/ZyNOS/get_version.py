# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Zyxel.ZyNOS.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
##
## SNMP OIDs to get FW version for some platforms
##
FW_OIDS = {
    "GS-3012": 10,
    "GS-3012F": 11,
    "ES-3124": 12,
    "GS-4024": 13,
    "GS-2024": 15,
    "ES-2024A": 16,
    "ES-2108": 18,
    "ES-2108-G": 19,
    "GS-4012F": 20,
    "ES-4124": 24,
    "XGS-4728F": 46,
    "GS2200-24": 55
}


class Script(BaseScript):
    name = "Zyxel.ZyNOS.get_version"
    cache = True
    interface = IGetVersion

    rx_fwver = re.compile(r"^ZyNOS F/W Version\s+:\s+V?(?P<version>\S+).+$",
                re.MULTILINE)
    rx_platform = re.compile(r"^Product Model\s+:\s+(?P<platform>\S+)$",
                re.MULTILINE)
    rx_prom = re.compile(r"^Bootbase Version\s+:\s+V?(?P<bootprom>\S+).+$",
                re.MULTILINE)

    def execute(self):
        if self.has_snmp():
            try:
                # Get platform from sys.Descr.0
                platform = self.snmp.get("1.3.6.1.2.1.1.1.0", cached=True)
                oid = FW_OIDS.get(platform)
                # Get major and minor versions, model string
                # and version control number
                if oid:
                    fwmaj = self.snmp.get("1.3.6.1.4.1.890.1.5.8.%d.1.1.0"
                                            % oid)
                    fwmin = self.snmp.get("1.3.6.1.4.1.890.1.5.8.%d.1.2.0"
                                            % oid)
                    fwmod = self.snmp.get("1.3.6.1.4.1.890.1.5.8.%d.1.3.0"
                                            % oid)
                    fwver = self.snmp.get("1.3.6.1.4.1.890.1.5.8.%d.1.4.0"
                                            % oid)
                else:
                    self.logger.error("Cannot find base OID for model '%s'"
                                % platform)
                    raise self.snmp.TimeOutError  # Fallback to CLI
                return {
                    "vendor": "Zyxel",
                    "platform": platform,
                    "version": "%s.%s(%s.%s)" % (fwmaj, fwmin, fwmod, fwver),
                }
            except self.snmp.TimeOutError:
                pass

        cmd = self.cli("show system-information", cached=True)
        r = {
            "vendor": "Zyxel",
            "version": "Unsupported",
            "platform": "Unsupported",
        }
        match = self.rx_fwver.search(cmd)
        if match:
            r["version"] = match.group("version")
        match = self.rx_platform.search(cmd)
        if match:
            r["platform"] = match.group("platform")
        match = self.rx_prom.search(cmd)
        if match:
            r["attributes"] = {"Boot PROM": match.group("bootprom")}
        return r
