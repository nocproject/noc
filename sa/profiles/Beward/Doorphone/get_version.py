# ---------------------------------------------------------------------
# Beward.Doorphone.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
from noc.core.mib import mib


class Script(BaseScript):
    name = "Beward.Doorphone.get_version"
    interface = IGetVersion
    cache = True

    def normalize(self, responce: str) -> tuple:
        """
        Normalized params in responce:
        'Beward IP Doorphone DKS, 66030, DKS850430_rev5.3.2.2.2, 3.5.0.0.1.25.46'

        :param: responce
        :return: (platform, version, image) without spaces
        """
        a, _, b, c = responce.split(",")
        a = (" ").join(a.split(" ")[:3]) + b.split("_")[0]
        b = b.split("_")[1]
        return a.strip(), b.strip(), c.strip()

    def execute_snmp(self):
        responce = self.snmp.get(mib["SNMPv2-MIB::sysDescr", 0])
        if responce:
            platform, version, image = self.normalize(responce)
            r = {
                "vendor": "Beward",
                "platform": platform or "",
                "version": version or "",
                "image": image or "",
            }
            return r
