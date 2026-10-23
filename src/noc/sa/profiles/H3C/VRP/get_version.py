# ---------------------------------------------------------------------
# H3C.VRP.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
from noc.core.mib import mib


class Script(BaseScript):
    name = "H3C.VRP.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(
        r"^.*?Switch\s(?P<platform>.+?)\sSoftware\s\\Version\s3Com\sOS\sV(?P<version>.+?)$",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    rx_ver1 = re.compile(
        r"^\s*Comware\sSoftware,\s(\\|)Version\s(?P<version>.+?),\s"
        r"(Release)?(?P<release>\w+(\s)?\w+).*(H3C ).*?(?P<platform>[a-zA-Z0-9\-]+) uptime is",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    rx_ver2 = re.compile(
        r"Version\s(?P<version>.+?), Release (?P<release>\S+)\n"
        r"[\S\s]+Quidway(?: Series Router)?\s(?P<platform>[a-zA-Z0-9\-]+) uptime is"
    )
    rx_hw = re.compile(r"Hardware Version is (?P<hardware>\S+)")
    rx_boot = re.compile(r"Bootrom Version is (?P<bootprom>\S+)")

    def execute_cli(self, **kwargs):
        v = self.cli("display version")
        snmp_sn1 = (
            self.snmp.get(mib["ENTITY-MIB::entPhysicalSerialNum.1"]) if self.has_snmp() else None
        )
        snmp_sn2 = (
            self.snmp.get(mib["ENTITY-MIB::entPhysicalSerialNum.2"]) if self.has_snmp() else None
        )
        match = self.rx_ver.search(v)
        if not match:
            match_re_list = [self.rx_ver1, self.rx_ver2]
            try:
                rx = self.find_re(match_re_list, v)
            except self.UnexpectedResultError:
                raise NotImplementedError
            match = rx.search(v)
            r = {
                "vendor": "H3C",
                "platform": match.group("platform"),
                "version": match.group("version") + "." + match.group("release"),
            }
        else:
            r = {
                "vendor": "H3C",
                "platform": match.group("platform"),
                "version": match.group("version"),
            }
        hw = self.rx_hw.search(v)
        boot = self.rx_boot.search(v)
        r["attributes"] = {}
        if snmp_sn1:
            r["attributes"]["Serial Number"] = snmp_sn1
        elif snmp_sn2:
            r["attributes"]["Serial Number"] = snmp_sn2
        if hw:
            r["attributes"]["HW version"] = hw.group("hardware")
        if boot:
            r["attributes"]["Boot PROM"] = boot.group("bootprom")
        return r
