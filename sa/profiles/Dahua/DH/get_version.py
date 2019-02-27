# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Dahua.DH.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Dahua.DH.get_version"
    cache = True
    interface = IGetVersion
    attr_api_map = {
        "platform": "magicBox.getDeviceType",
        "version": "magicBox.getSerialNo",
        "serial": "magicBox.getSerialNo",
        "PTZ ver.": "",
        "hw. type": "magicBox.getHardwareType",
    }

    def execute(self):
        system_info = self.http.get("/cgi-bin/magicBox.cgi?action=getSystemInfo")
        system_info = self.profile.parse_equal_output(system_info)
        software_version = self.http.get("/cgi-bin/magicBox.cgi?action=getSoftwareVersion")
        software_version = self.profile.parse_equal_output(software_version)
        version, build = software_version["version"].split(",")
        build = build.split(":")[1]
        # print(software_version)

        return {
            "vendor": "Dahua",
            "platform": system_info["deviceType"],
            "version": version,
            "attributes": {
                # "Boot PROM": match.group("bootprom"),
                "Build Date": build,
                "HW version": system_info["hardwareVersion"],
                "Serial Number": system_info["serialNumber"]
                # "Firmware Type":
            }
        }
