# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Raisecom
# OS:     ROS
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.profile.base import BaseProfile
from noc.core.confdb.syntax.patterns import ANY


class Profile(BaseProfile):
    name = "Raisecom.ROS"
    pattern_more = r"^ --More--\s*"
    pattern_unprivileged_prompt = r"^\S+?>"
    command_super = "enable"
    pattern_prompt = r"^\S+?#"
    command_more = " "
    command_exit = "exit"
    pattern_syntax_error = r"% \".+\"  (?:Unknown command.)|Error input in the position marked by"
    pattern_operation_error = r"% You Need higher priority!"
    rogue_chars = [re.compile(r"\x08+\s+\x08+"), "\r"]
    config_volatile = [
        r"radius(-server | accounting-server |-)encrypt-key \S+\n",
        r"tacacs(-server | accounting-server |-)encrypt-key \S+\n",
    ]
    config_tokenizer = "context"
    config_tokenizer_settings = {
        "line_comment": "!",
        "contexts": [["interface", ANY, ANY]],
        "end_of_context": "!",
    }

    matchers = {"is_iscom2624g": {"platform": {"$regex": "ISCOM26(?:24|08)G"}}}

    # Version until ROS_4.15.1086.ISCOM2128EA-MA-AC.002.20151224
    rx_ver = re.compile(
        r"Product name: (?P<platform>\S+)\s*\n"
        r"(ROS|QOS)\s+Version\s*(?P<version>\S+)\.\s*\(Compiled.+\)\s*\n"
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
        r"(ROS|QOS)\s+Version\s*(?P<version>\S+)\.\s*\(Compiled.+\)\s*\n"
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
        r"(ROS|QOS)\s+Version(:|)\s*(?P<version>\S+)(\.|)\s*\(Compiled.+\)\s*\n"
        r"Bootstrap\s*Version(:|)\s*(?P<bootstrap>\S+)\s*\n"
        r"Hardware\s*\S*\s*Version(\sRev\.|:)\s*(?P<hw_rev>\S+)\s*\n\n"
        r"System MacAddress is\s*:\s*(?P<mac>\S+)\s*\n"
        r"Serial number\s*:\s*(?P<serial>\S+)\s*",
        re.MULTILINE | re.IGNORECASE,
    )

    # Version start  ROS_5.1.1.420 (Compiled May 15 2015, 12:36:24)
    rx_ver_2015 = re.compile(
        r"Product name: (?P<platform>\S+)\s*\n"
        r"(ROS|QOS)\s+Version(:|)\s*(?P<version>\S+)(\.|)\s*\(Compiled.+\)\s*\n"
        r"Product Version: \S+\s*\n"
        r"BOOT Room Version\s*(:|)\s*(?P<bootstrap>\S+)\s*\n"
        r"CPLD Version: \S+\s*\n"
        r"Hardware\s*\S*\s*Version(\sRev\.|:)?\s*(?P<hw_rev>\S+)\s*\n\n"
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

    rx_ver_rotek = re.compile(r"Rotek Operating System Software\n" r"Copyright .+NPK Rotek")

    # NPK Rotek some Chinese vendor
    def get_version(self, script):
        c = script.cli("show version", cached=True)
        r = {"vendor": "Raisecom"}
        if self.rx_ver_rotek.match(c):
            r["vendor"] = "Rotek"
        if "Support ipv6" in c:
            match = self.rx_ver.search(c)
        else:
            match = self.rx_ver_wipv6.search(c)
        if match:
            r.update(match.groupdict())
            return r
        else:
            match = self.rx_ver2.search(c)
        if match:
            r.update(match.groupdict())
            return r
        else:
            match = self.rx_ver_2016.search(c)
        if match:
            r.update(match.groupdict())
            return r
        else:
            match = self.rx_ver_2015.search(c)
        if match:
            r.update(match.groupdict())
            return r
        else:
            match = self.rx_ver_2017.search(c)
        if match:
            r.update(match.groupdict())
            return r
        else:
            match = self.rx_ver3.search(c)
        r.update(match.groupdict())
        return r

    rx_port = re.compile(r"^port(|\s+)(?P<port>\d+)")

    def convert_interface_name(self, interface):
        if interface.startswith("GE"):
            return interface.replace("GE", "gigaethernet")
        if interface.startswith("FE"):
            return interface.replace("FE", "fastethernet")
        if self.rx_port.match(interface):
            match = self.rx_port.match(interface)
            return match.group("port")
        else:
            return interface
