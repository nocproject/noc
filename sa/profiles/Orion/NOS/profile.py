# ---------------------------------------------------------------------
# Vendor: Orion (Orion Networks)
# OS:     NOS
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Orion.NOS"

    pattern_unprivileged_prompt = rb"^(?P<hostname>\S+)\s*>"
    pattern_prompt = rb"^(?P<hostname>\S+)\s*#"
    pattern_syntax_error = rb"^% \" .+ \"  Unknown command."
    command_super = b"enable"
    command_disable_pager = "terminal page-break disable"
    pattern_more = [(rb" --More-- ", b" ")]
    command_exit = "exit"
    config_volatile = [
        r"radius(-| accounting-server )encrypt-key \S+\n",
        r"tacacs(-server | accounting-server )encrypt-key \S+\n",
    ]

    rx_interface_name = re.compile(r"(?:port\s*|P)(?P<re_port>\d+)")

    rx_ver = re.compile(
        r"^Product name\s*:\s*(?P<platform>.+)\s*\n"
        r"^NOS\s+Version:? NOS_(?P<version>\d+\.\d+\.\d+).+\n"
        r"(^Support ipv6\s*:\s*(?P<ipv6_support>\S+)\s*\n)?"
        r"^Bootstrap\s+Version:? (?P<bootprom>(Bootstrap_\d+\.\d+\.\d+|UNKNOWN)).*\n"
        r"(^FPGA Version\s*\n)?"
        r"^Hardware( \S+| \S+\s\S+|) Version( Rev.|\: ?|\s*)(?P<hardware>\S+)\s*(\nCPLD Version: 1.0)?\n*"
        r"\n"
        r"^System MacAddress is\s*:\s*(?P<mac>\S+)\s*\n"
        r"^Serial number\s*:\s*(?P<serial>\S+)\s*\n",
        re.MULTILINE,
    )

    rx_ver2 = re.compile(
        r"^Product Name\s*:\s*(?P<platform>.+)\s*\n"
        r"^Hardware Version: (?P<hardware>\S+)\s*\n"
        r"^Software Version: NOS_(?P<version>\d+\.\d+\.\d+).+\n"
        r"(^PCB Version.+\n)?"
        r"(^CPLD Version.+\n)?"
        r"(^NOS Version.+\n)?"
        r"^Bootstrap Version: (?P<bootprom>\d+\.\d+\.\d+).*\n"
        r"(^Compiled.+\n)?"
        r"\s*\n"
        r"^System MacAddress:\s*(?P<mac>\S+)\s*\n"
        r"^Serial number:\s*(?P<serial>\S+)\s*\n",
        re.MULTILINE,
    )

    rx_ver3 = re.compile(
        r"^\s+Orion (?P<platform>Alpha \S+) Device, Compiled on .+\s*\n"
        r"^\s+sysLocation .+\n"
        r"^\s+CPU Mac (?P<mac>\S+)\s*\n"
        r"^\s+Vlan MAC (?P<mac2>\S+)\s*\n"
        r"^\s+SoftWare Version (?P<version>\S+)\s*\n"
        r"^\s+BootRom Version (?P<bootprom>\S+)\s*\n"
        r"^\s+HardWare Version (?P<hardware>\S+)\s*\n"
        r"(^\s+CPLD Version.+\n)?"
        r"^\s+Serial No.:\s*(?P<serial>\S+)\s*\n",
        re.MULTILINE,
    )

    rx_port = re.compile(r"^\s*P?(?P<port>\d+)\s+", re.MULTILINE)

    matchers = {
        "is_beta": {"platform": {"$regex": r"^Beta-"}},
        "is_a26": {"platform": {"$regex": r"^Alpha A26"}},
    }

    def get_version(self, script):
        c = script.cli("show version", cached=True)
        match = self.rx_ver.search(c)
        if not match:
            match = self.rx_ver2.search(c)
            if not match:
                match = self.rx_ver3.search(c)
        return match.groupdict()

    def get_port_count(self, script):
        c = script.cli("show port-security", cached=True)
        return len(self.rx_port.findall(c))

    def convert_interface_name(self, s):
        if self.rx_interface_name.match(s):
            return self.rx_interface_name.match(s).group("re_port")
        return s

    INTERFACE_TYPES = {
        "Et": "physical",  # Ethernet
        "Vl": "SVI",  # Vlan
    }

    @classmethod
    def get_interface_type(cls, name):
        return cls.INTERFACE_TYPES.get(name[:2])
