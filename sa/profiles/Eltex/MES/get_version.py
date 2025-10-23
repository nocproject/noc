# ---------------------------------------------------------------------
# Eltex.MES.get_version
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
    name = "Eltex.MES.get_version"
    interface = IGetVersion
    cache = True

    rx_version1 = re.compile(r"^SW version+\s+(?P<version>\S+)", re.MULTILINE)
    rx_version2 = re.compile(
        r"^Active-image: (?P<image>\S+)\s*\n^\s+Version: (?P<version>\S+)", re.MULTILINE
    )
    rx_bootprom = re.compile(r"^Boot version+\s+(?P<bootprom>\S+)", re.MULTILINE)
    rx_hardware = re.compile(r"^HW version+\s+(?P<hardware>\S+)$", re.MULTILINE)
    rx_serial1 = re.compile(r"^Serial number :\s+(?P<serial>\S+)$", re.MULTILINE)
    rx_serial2 = re.compile(r"^\s+1\s+(?P<serial>\S+)\s*\n", re.MULTILINE)
    rx_serial3 = re.compile(
        r"^\s+1\s+(?P<mac>\S+)\s+(?P<hardware>\S+)\s+(?P<serial>\S+)\s*\n", re.MULTILINE
    )
    rx_master_unit = re.compile(r"^\s*(?P<unit>\d+)\s+.+\s+master\s*\n", re.MULTILINE)
    rx_platform = re.compile(r"^System Object ID:\s+(?P<platform>\S+)$", re.MULTILINE)

    def execute_snmp(self, **kwargs):
        try:
            platform = self.snmp.get(mib["SNMPv2-MIB::sysObjectID", 0], cached=True)
            platform = platform.split(".")[8]
            platform, revision = self.profile.get_platform(platform.split(")")[0])
            version = self.snmp.get(mib["ENTITY-MIB::entPhysicalSoftwareRev", 67108992])
            try:
                bootprom = self.snmp.get(mib["ENTITY-MIB::entPhysicalFirmwareRev", 67108992])
            except self.snmp.SNMPError:
                bootprom = None
            try:
                hardware = self.snmp.get(mib["ENTITY-MIB::entPhysicalHardwareRev", 67108992])
            except self.snmp.SNMPError:
                hardware = None
            serial = self.snmp.get(mib["ENTITY-MIB::entPhysicalSerialNum", 67108992])
            if not version:
                # rndBrgVersion
                version = self.snmp.get("1.3.6.1.4.1.89.2.4.0", cached=True)
            if not serial:
                # rlPhdUnitGenParamSerialNum
                serial = self.snmp.get("1.3.6.1.4.1.89.53.14.1.5.1", cached=True)
            r = {
                "vendor": "Eltex",
                "platform": platform,
                "version": version,
                "attributes": {
                    "Serial Number": serial,
                },
            }
            if bootprom:
                r["attributes"]["Boot PROM"] = bootprom
            if hardware:
                r["attributes"]["HW version"] = hardware
            if revision:
                r["attributes"]["revision"] = revision
            return r
        except self.snmp.TimeOutError:
            raise self.UnexpectedResultError

    def execute_cli(self, **kwargs):
        try:
            v = self.cli("show unit", cached=True)
        except self.CLISyntaxError:
            v = self.cli("show stack", ignore_errors=True, cached=True)
        match = self.rx_master_unit.search(v)
        if match:
            master_unit = match.group("unit")
            plat = self.cli("show system unit %s" % master_unit, cached=True)
            try:
                ver = self.cli("show version unit %s" % master_unit, cached=True)
            except self.CLISyntaxError:
                ver = self.cli("show version", cached=True)
            ser = self.cli("show system id unit %s" % master_unit, cached=True)
        else:
            plat = self.cli("show system", cached=True)
            ver = self.cli("show version", cached=True)
            ser = self.cli("show system id", cached=True)

        match = self.rx_platform.search(plat)
        platform = match.group("platform")
        platform = platform.split(".")[8]
        platform, revision = self.profile.get_platform(platform)

        match = self.rx_version1.search(ver)
        if match:
            version = self.rx_version1.search(ver)
            bootprom = self.rx_bootprom.search(ver)
            hardware = self.rx_hardware.search(ver)
            image = None
        else:
            version = self.rx_version2.search(ver)
            bootprom = None
            hardware = None
            image = version.group("image").split("/")[-1]

        match = self.rx_serial1.search(ser)
        match2 = self.rx_serial3.search(ser)
        if match:
            serial = self.rx_serial1.search(ser)
        elif match2:
            # Unit    MAC address    Hardware version Serial number
            # ---- ----------------- ---------------- -------------
            # 1   xx:xx:xx:xx:xx:xx     02.01.02      ESXXXXXXX
            serial = self.rx_serial3.search(ser)
        else:
            serial = self.rx_serial2.search(ser)

        res = {
            "vendor": "Eltex",
            "platform": platform,
            "version": version.group("version").split("[")[0],
            "attributes": {},
        }

        if image:
            res["image"] = image
        if serial:
            res["attributes"]["Serial Number"] = serial.group("serial")
        if bootprom:
            res["attributes"]["Boot PROM"] = bootprom.group("bootprom")
        if hardware:
            res["attributes"]["HW version"] = hardware.group("hardware")
        if revision:
            res["attributes"]["revision"] = revision
        return res
