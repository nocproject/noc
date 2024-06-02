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

    def get_ptz_version(self):
        """
        Getting PTZ SW version from WEB:
        POST, /RPC2, {"method": "magicBox.getSubModules", "params": null}
        Response {"id":194,"params":{"subModules":[
        {"HardwareVersion":"Unknow","ModuleName":"PTZ","SoftwareVersion":"3.01.35.RHNT","State":"Normal"},
        {"HardwareVersion":"Unknow","ModuleName":"Camera","SoftwareVersion":"Unknow","State":"Normal"}]},
        "result":true,"session":43241591}
        :return: PTZ Driver Version
        :rtype: str
        """
        r = self.http.post(
            "/RPC2", data={"method": "magicBox.getSubModules", "params": None}, json=True
        )
        # @todo add PTZ to caps
        if "subModules" in r["params"] and r["params"]["subModules"]:
            for sm in r["params"]["subModules"]:
                if sm["ModuleName"] == "PTZ":
                    return sm["SoftwareVersion"]
        return None

    def execute(self):
        system_info = self.http.get("/cgi-bin/magicBox.cgi?action=getSystemInfo")
        system_info = self.profile.parse_equal_output(system_info)
        software_version = self.http.get("/cgi-bin/magicBox.cgi?action=getSoftwareVersion")
        software_version = self.profile.parse_equal_output(software_version)
        version, build = software_version["version"].split(",")
        build = build.split(":")[1]

        attributes = {
            # "Boot PROM": match.group("bootprom"),
            "Build Date": build,
            "HW version": system_info["hardwareVersion"],
            "Serial Number": system_info["serialNumber"],
            # "Firmware Type":
        }
        vendor = "Dahua"
        if system_info["deviceType"].startswith("RVi"):
            vendor = "RVi"
        if vendor == "Dahua":
            ptz = self.get_ptz_version()
            if ptz:
                attributes["PTZ version"] = ptz
        return {
            "vendor": vendor,
            "platform": system_info["deviceType"],
            "version": version,
            "attributes": attributes,
        }
