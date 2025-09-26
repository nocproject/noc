# ---------------------------------------------------------------------
# Qtech.QSW2800.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
from noc.core.mib import mib
from noc.core.text import parse_kv


class Script(BaseScript):
    name = "Qtech.QSW2800.get_version"
    interface = IGetVersion
    cache = True
    always_prefer = "S"

    rx_ver = re.compile(
        r"^\s*(?:Device: )?(?P<platform>\S+)(?: Device|, sysLocation\:|).*\n"
        r"^\s*SoftWare(?: Package)? Version\s+(?P<version>\S+(?:\(\S+\))?)\n"
        r"^\s*BootRom Version\s+(?P<bootprom>\S+)\n"
        r"^\s*HardWare Version\s+(?P<hardware>\S+).+"
        r"^\s*(?:Device serial number |Serial No.:(?:|\s+))(?P<serial>\S+|\S+pn sw)\n",
        # pn sw on serial - QSW-3500-10T-AC, 8.2.1.52
        re.MULTILINE | re.DOTALL,
    )

    rx_ver2 = re.compile(
        r"^\s*SoftWare(?: Package)? Version\s+(?P<version>\S+(?:\(\S+\))?)\n"
        r"^\s*BootRom Version\s+(?P<bootprom>\S+)\n"
        r"^\s*HardWare Version\s+(?P<hardware>\S+).+"
        r"^\s*(?:Device serial number |Serial No.:(?:|\s))(?P<serial>\S+)\n",
        re.MULTILINE | re.DOTALL,
    )

    rx_ver3 = re.compile(
        r"(?P<platform>\S+),\s*(?P<platform_description>.+),"
        r"\s*(?P<version>\S+),\s+Linux (?P<linux_version>\S+)"
    )

    rx_vendor = re.compile(r"^DeviceOid\s+\d+\s+(?P<oid>\S+)", re.MULTILINE)
    rx_version = re.compile(r"Software, Version (?P<version>\S+),")

    qtech_platforms = {
        "1.3.6.1.4.1.6339.1.1.1.48": "QSW-2800",
        "1.3.6.1.4.1.6339.1.1.1.49": "QSW-2800",
        "1.3.6.1.4.1.6339.1.1.1.228": "QSW-3450-28T-AC",
        "1.3.6.1.4.1.6339.1.1.1.3": "QSW-3470-28T-AC",
        "1.3.6.1.4.1.6339.1.1.1.244": "S5750E-28X-SI-24F-D",
        "1.3.6.1.4.1.6339.1.1.1.301": "QSW-3470-10T-AC-POE",
        "1.3.6.1.4.1.6339.1.1.1.310": "QSW-4610-28T-AC",
        "1.3.6.1.4.1.6339.1.1.2.40": "QSW-8300-52F",
        "1.3.6.1.4.1.6339.1.1.2.59": "QSW-8200-28F-AC-DC",
        "1.3.6.1.4.1.13464.1.3.13": "QSW-2900-24T",
        "1.3.6.1.4.1.13464.1.3.26.7": "QSW-2910",
        "1.3.6.1.4.1.27514": "QSW-8200–28F-AC-DC rev.Q1",  # Bad lifehack
        "1.3.6.1.4.1.27514.1.1.1.39": "QSW-2800-26T-AC",
        "1.3.6.1.4.1.27514.1.1.1.48": "QSW-2800-10T-AC",
        "1.3.6.1.4.1.27514.1.1.1.49": "QSW-2800-28T-AC",
        "1.3.6.1.4.1.27514.1.1.1.52": "QSW-2800-28T-AC-RPS",
        "1.3.6.1.4.1.27514.1.1.1.53": "QSW-2800-28T-DC",
        "1.3.6.1.4.1.27514.1.1.1.220": "QSW-3400-10T-AC",
        "1.3.6.1.4.1.27514.1.1.1.221": "QSW-3400-28T-AC",
        "1.3.6.1.4.1.27514.1.1.1.234": "QSW-8200-28F-AC-DC",
        "1.3.6.1.4.1.27514.1.1.1.235": "QSW-8200-28F-AC-DC",
        "1.3.6.1.4.1.27514.1.1.1.248": "QSW-3450-28T-POE-AC",
        "1.3.6.1.4.1.27514.1.1.1.280": "QSW-3750-52T-AC",
        "1.3.6.1.4.1.27514.1.1.1.282": "QSW-3470-10T-AC",
        "1.3.6.1.4.1.27514.1.1.1.299": "QSW-3750-28T-AC",
        "1.3.6.1.4.1.27514.1.1.1.310": "QSW-3580-28T-AC",
        "1.3.6.1.4.1.27514.1.1.1.337": "QSW-2850-28T-AC",
        "1.3.6.1.4.1.27514.1.1.1.350": "QSW-4610-10T-AC",
        "1.3.6.1.4.1.27514.1.1.1.354": "QSW-3470-28T-AC-POE",
        "1.3.6.1.4.1.27514.1.1.1.355": "QSW-3750-28T-AC",
        "1.3.6.1.4.1.27514.1.1.1.356": "QSW-3470-10T-AC-POE",
        "1.3.6.1.4.1.27514.1.1.1.339": "QSW-2850-18T-AC",
        "1.3.6.1.4.1.27514.1.1.1.351": "QSW-3500-10T-AC",
        "1.3.6.1.4.1.27514.1.1.1.407": "QSW-3470-10T-AC",
        "1.3.6.1.4.1.27514.1.1.1.422": "QSW-3470-10T-AC-POE",
        "1.3.6.1.4.1.27514.1.1.2.39": "QSW-8200-28F",
        "1.3.6.1.4.1.27514.1.1.2.40": "QSW-8300",
        "1.3.6.1.4.1.27514.1.1.2.53": "QSW-8200-28F-AC-DC",
        "1.3.6.1.4.1.27514.1.1.2.59": "QSW-8200-28F-AC-DC",
        "1.3.6.1.4.1.27514.1.1.2.60": "QSW-8270-28F-AC",
        "1.3.6.1.4.1.27514.1.3.13": "QSW-2900-24T",
        "1.3.6.1.4.1.27514.1.3.13.0": "QSW-2900",
        "1.3.6.1.4.1.27514.1.3.26.2": "QSW-3900",
        "1.3.6.1.4.1.27514.1.3.26.1": "QSW-3900",
        "1.3.6.1.4.1.27514.1.3.25.2": "QSW-2900-24T4",
        "1.3.6.1.4.1.27514.1.3.26.7": "QSW-2910-28F",
        "1.3.6.1.4.1.27514.1.3.26.8": "QSW-2910-28T-POE",
        "1.3.6.1.4.1.27514.1.3.26.9": "QSW-2910-10T-POE",
        "1.3.6.1.4.1.27514.1.3.32.1": "QSW-2910-26T",
        "1.3.6.1.4.1.27514.1.3.32.3": "QSW-2910-09T-POE",
        "1.3.6.1.4.1.27514.1.280": "QSW-2870-10T",
        "1.3.6.1.4.1.27514.1.287": "QSW-2870-28T",
        "1.3.6.1.4.1.27514.1.282803": "QSW-2800-28T",
        "1.3.6.1.4.1.27514.3.2.10": "QSW-3470-10T-AC",
        "1.3.6.1.4.1.27514.6.55": "QSW-2500E",
        "1.3.6.1.4.1.27514.101": "QFC-PBIC",
        "1.3.6.1.4.1.27514.102.1.2.40": "QSW-8300-52F",
    }

    def fix_platform(self, platform: str) -> str:
        """
        For customize
        :param platform:
        :return:
        """
        return platform

    def get_platform_by_sysoid(self, oid: str) -> str:
        if oid.startswith("."):
            oid = oid[1:]
        # self.snmp.get(mib[".1.3.6.1.4.1.27514.1.1.1.1.1.1", 0], cached=True)
        platform = self.qtech_platforms.get(oid)
        if platform is None:
            self.logger.info("Unknown platform OID: %s" % oid)
            raise NotImplementedError("Unknown platform OID: %s" % oid)
        if oid == "1.3.6.1.4.1.27514.1.1.1.310":
            # Both QSW-3580-28T-AC and QSW-3470-28T-AC has same OID
            temp = self.snmp.get(mib["ENTITY-MIB::entPhysicalModelName", 1])
            if temp is not None and temp != "QSW-3580-28T-AC":
                platform = "QSW-3470-28T-AC"
        return platform

    def fix_hw_serial(self):
        serial, hw_ver = None, None
        try:
            # SNMPv2-MIB::sysDescr.0
            serial = self.snmp.get(mib["1.3.6.1.4.1.27514.1.1.1.1.1.4.0"])
            hw_ver = self.snmp.get(mib["1.3.6.1.4.1.27514.1.1.1.1.1.6.0"])
        except (self.snmp.TimeOutError, self.snmp.SNMPError):
            pass
        return serial, hw_ver

    def execute_snmp(self, **kwargs):
        r = {"vendor": "Qtech", "attributes": {}}
        sys_descr = self.snmp.get(mib["SNMPv2-MIB::sysDescr", 0], cached=True)
        sys_descr = sys_descr.replace("\x16", "")  # On QSW-3400-28T-AC 7.0.3.5(B0221.0055)
        for ree in [self.rx_ver, self.rx_ver2, self.rx_ver3]:
            match = ree.match(sys_descr)
            if match:
                match = match.groupdict()
                if "platform" in match:
                    r["platform"] = match["platform"]
                r["version"] = match["version"]
                break
        if not match or "platform" not in match or match["platform"] == "Switch":
            oid = self.snmp.get(mib["SNMPv2-MIB::sysObjectID", 0])
            r["platform"] = self.get_platform_by_sysoid(oid)
        r["platform"] = self.fix_platform(r["platform"])
        if "version" not in r and sys_descr:
            r["version"] = self.rx_version.search(sys_descr).group("version")
        if match and "bootprom" in match:
            r["attributes"]["Boot PROM"] = match["bootprom"]
        hw_ver, serial = self.fix_hw_serial()
        if match and "hardware" in match:
            r["attributes"]["HW version"] = match["hardware"]
        elif hw_ver:
            r["attributes"]["HW version"] = hw_ver
        if match and "serial" in match:
            r["attributes"]["Serial Number"] = match["serial"].replace(
                "\x1b7", ""
            )  # On QSW-4610-10T-AC 8.2.1.60
        elif serial:
            r["attributes"]["Serial Number"] = serial
        if "version" not in r:
            raise NotImplementedError
        return r

    info_map = {
        "firmware version": "fw_ver",
        "firmware date": "fw_date",
        "system object id": "sysid",
    }

    def get_info(self):
        # For QSW-3470-10T  3.0.1-R1-BETA3 fw
        try:
            v = self.cli("show info")
        except self.CLISyntaxError:
            return {}
        r = parse_kv(self.info_map, v, ":")
        platform = self.get_platform_by_sysoid(r["sysid"])
        return {
            "vendor": "Qtech",
            "platform": platform,
            "version": "%s (%s)" % (r["fw_ver"], r["fw_date"]),
        }

    def execute_cli(self, **kwargs):
        ver = self.cli("show version", cached=True)
        match = self.rx_ver.search(ver)
        if match:
            platform = match.group("platform").strip(" ,")
            version = match.group("version")
            bootprom = match.group("bootprom")
            hardware = match.group("hardware")
            serial = match.group("serial")
            if platform == "Switch":
                try:
                    # Hidden command !!!
                    v = self.cli("show vendor")
                    match = self.rx_vendor.search(v)
                    if match:
                        platform = self.get_platform_by_sysoid(match.group("oid"))
                except self.CLISyntaxError:
                    pass
            return {
                "vendor": "Qtech",
                "platform": self.fix_platform(platform),
                "version": version,
                "attributes": {
                    "Boot PROM": bootprom,
                    "HW version": hardware,
                    "Serial Number": serial,
                },
            }
        # For QSW-3470-10T  3.0.1-R1-BETA3 fw
        r = self.get_info()
        if r:
            return r
        raise NotImplementedError("Unknown platform")
