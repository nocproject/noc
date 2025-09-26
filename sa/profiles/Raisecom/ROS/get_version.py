# ---------------------------------------------------------------------
# Raisecom.ROS.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
from noc.core.text import parse_kv


class Script(BaseScript):
    name = "Raisecom.ROS.get_version"
    interface = IGetVersion
    cache = True

    # Version until ROS_4.15.1086.ISCOM2128EA-MA-AC.002.20151224
    rx_ver = re.compile(
        r"Product name: (?P<platform>\S+)\s*\n"
        r"(ROS|QOS)\s+Version\s*(?P<version>\S+)\.\s*\(Compiled(?P<compiled>.+)\)\s*\n"
        r"(Support ipv6\s*:\s*\S+\s*\n)?"
        r"Bootstrap\s*Version\s*(?P<bootstrap>\S+)\s*\n"
        r"FPGA Version\s*\n"
        r"Hardware\s*\S+\s*Version Rev\.\s*(?P<hw_rev>\S+)\s*\n\n"
        r"System MacAddress is\s*:\s*(?P<mac>\S+)\s*\n"
        r"Serial number\s*:\s*(?P<serial>\S+)\s*\n",
        re.MULTILINE,
    )

    rx_ver_wipv6 = re.compile(
        r"Product name: (?P<platform>\S+)\s*\n"
        r"(ROS|QOS)\s+Version\s*(?P<version>\S+)\.\s*\(Compiled(?P<compiled>.+)\)\s*\n"
        r"Bootstrap\s*Version\s*(?P<bootstrap>\S+)\s*\n"
        r"FPGA Version\s*\n"
        r"Hardware\s*\S+\s*Version Rev\.\s*(?P<hw_rev>\S+)\s*\n\n"
        r"System MacAddress is\s*:\s*(?P<mac>\S+)\s*\n"
        r"Serial number\s*:\s*(?P<serial>\S+)\s*\n",
        re.MULTILINE,
    )

    rx_ver2 = re.compile(
        r"Product Name: (?P<platform>\S+)\s*\n"
        r"Hardware Version: (?P<hw_rev>\S+)\s*\n"
        r"Bootstrap Version: (?P<bootstrap>\S+)\s*\n"
        r"Software Version: (?P<version>\S+)\s*\n"
        r"PCB Version:.+\n"
        r"(FPGA Version:.+\n)?"
        r"CPLD Version:.+\n"
        r"REAP Version:.+\n"
        r"Compiled.+\n\n"
        r"System MacAddress: (?P<mac>\S+)\s*\n"
        r"Serial number: (?P<serial>\S+)\s*\n",
        re.MULTILINE,
    )

    rx_ver3 = re.compile(
        r"Product Name: (?P<platform>\S+)\s*\n"
        r"Hardware Version: (?P<hw_rev>\S+)\s*\n"
        r"Software Version: (?P<version>\S+)\s*\n"
        r"PCB Version:.+\n"
        r"(FPGA Version:.+\n)?"
        r"CPLD Version:.+\n"
        r"REAP Version:.+\n"
        r"Bootstrap Version: (?P<bootstrap>\S+)\s*\n"
        r"Compiled.+\n\n"
        r"System MacAddress: (?P<mac>\S+)\s*\n"
        r"Serial number: (?P<serial>\S+)\s*\n",
        re.MULTILINE,
    )

    # Version start  ROS_4.15.1200_20161130(Compiled Nov 30 2016, 10:51:45)
    rx_ver_2016 = re.compile(
        r"Product name: (?P<platform>\S+)\s*\n"
        r"(ROS|QOS)\s+Version(:|)\s*(?P<version>\S+)(\.|)\s*\(Compiled(?P<compiled>.+)\)\s*\n"
        r"Bootstrap\s*Version(:|)\s*(?P<bootstrap>\S+)\s*\n"
        r"Hardware\s*\S*\s*Version(\sRev\.|:)\s*(?P<hw_rev>\S+)\s*\n\n"
        r"System MacAddress is\s*:\s*(?P<mac>\S+)\s*\n"
        r"Serial number\s*:\s*(?P<serial>\S+)\s*",
        re.MULTILINE | re.IGNORECASE,
    )

    # Version start  ROS_5.1.1.420 (Compiled May 15 2015, 12:36:24)
    rx_ver_2015 = re.compile(
        r"Product name:\s*(Gazelle |)(?P<platform>\S+)\s*\n"
        r"(ROS|QOS)\s+Version(:|)\s*(?P<version>\S+)(\.|)\s*\(Compiled(?P<compiled>.+)\)\s*\n"
        r"Product Version: \S+\s*\n"
        r"BOOT Room Version\s*(:|)\s*(Gazelle |)(?P<bootstrap>\S+)\s*\n"
        r"CPLD Version: \S+\s*\n"
        r"Hardware\s*(Gazelle |)\S*\s*Version(\sRev\.|:)?\s*(?P<hw_rev>\S+)\s*\n\n"
        r"System MacAddress( is)?\s*:\s*(?P<mac>\S+)\s*\n"
        r"Serial number\s*:\s*(?P<serial>\S+)\s*",
        re.MULTILINE | re.IGNORECASE,
    )

    # Version start  5.2.1_20171221
    rx_ver_2017 = re.compile(
        r"Product Name: (?P<platform>\S+)\s*\n"
        r"Hardware Version: (?P<hw_rev>\S+)\s*\n"
        r"Software Version:.+\n"
        r"ROS Version: (?P<version>\S+)\s*\n"
        r"REAP Version:.+\n"
        r"Bootrom Version: (?P<bootstrap>\S+)\s*\n\n"
        r"System MAC Address: (?P<mac>\S+)\s*\n"
        r"Serial number: (?P<serial>\S+)\s*",
        re.MULTILINE,
    )

    rx_ver_rotek = re.compile(r"Rotek Operating System Software\nCopyright .+NPK Rotek")

    rx_ver_qtech = re.compile(r"QTECH Universal Software Platform")

    kv_map = {
        "product name": "platform",
        "ros version": "version",
        "qos version": "version",
        "software version": "version",
        "bootstrap version": "bootstrap",
        "boot room version": "bootstrap",
        "bootrom version": "bootstrap",
        "hardware version": "hw_rev",
        "hardware version rev.": "hw_rev",
        "system macaddress is": "mac_address",
        "system macaddress": "mac_address",
        "system mac address": "mac_address",
        "serial number": "serial",
    }

    @classmethod
    def parse_kv_version(cls, v):
        r = parse_kv(cls.kv_map, v)
        if not r:
            raise NotImplementedError("Not supported platform output format")
        if "Gazelle" in r["platform"]:
            _, r["platform"] = r["platform"].split(None, 1)
        return r

    def parse_version(self, c):
        r = {}
        if "Support ipv6" in c:
            match = self.rx_ver.search(c)
        else:
            match = self.rx_ver_wipv6.search(c)
        if match:
            r.update(match.groupdict())
            return r
        match = self.rx_ver2.search(c)
        if match:
            r.update(match.groupdict())
            return r
        match = self.rx_ver_2016.search(c)
        if match:
            r.update(match.groupdict())
            return r
        match = self.rx_ver_2015.search(c)
        if match:
            r.update(match.groupdict())
            return r
        match = self.rx_ver_2017.search(c)
        if match:
            r.update(match.groupdict())
            return r
        match = self.rx_ver3.search(c)
        if not match:
            return self.parse_kv_version(c)
        return match.groupdict()

    # NPK Rotek some Chinese vendor
    def execute_cli(self):
        v = self.cli("show version", cached=True)
        vendor = "Raisecom"
        if self.rx_ver_rotek.search(v):
            vendor = "Rotek"
        elif self.rx_ver_qtech.search(v):
            # Universal Operating System ^_^
            vendor = "Qtech"
        r = self.parse_version(v)
        if vendor == "Rotek" and "compiled" in r:
            r["version"] = "%s (%s)" % (r["version"], r["compiled"].strip())
        return {
            "vendor": vendor,
            "platform": r["platform"],
            "version": r["version"],
            "attributes": {
                "Serial Number": r["serial"],
                "Boot PROM": r["bootstrap"],
                "HW version": r["hw_rev"],
            },
        }
