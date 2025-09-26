# ---------------------------------------------------------------------
# Rotek.RTBSv1.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
from noc.core.mib import mib


class Script(BaseScript):
    name = "Rotek.RTBSv1.get_version"
    cache = True
    interface = IGetVersion
    reuse_cli_session = False
    keep_cli_session = False
    always_prefer = "S"

    def execute_snmp(self, **kwargs):
        oid = self.snmp.get(mib["SNMPv2-MIB::sysDescr", 0], cached=True)
        platform = "%s.%s" % (oid.split(" ")[0].strip(), oid.split(" ")[1].strip())
        version = oid.split(" ")[2].strip()

        return {
            "vendor": "Rotek",
            "version": version,
            "platform": platform,
            # "attributes": {
            # "HW version": hwversion}
        }

    def execute_cli(self, **kwargs):
        try:
            c = self.cli("show software version")
        except self.CLISyntaxError:
            c = self.cli("show software-version")
        line = c.split(":")
        res = line[1].strip().split(".", 2)
        hwversion = "%s.%s" % (res[0], res[1])
        sw = res[2].strip()
        result = {"vendor": "Rotek", "version": sw, "attributes": {"HW version": hwversion}}
        with self.profile.shell(self):
            v = self.cli("cat /etc/product", cached=True)
            for line in v.splitlines():
                li = line.split(":", 1)
                if "productName" in li[0]:
                    platform = li[1].strip().replace(" ", ".").replace('"', "").replace(",", "")
                    result["platform"] = platform
        return result
